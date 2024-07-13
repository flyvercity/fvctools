import click
from pathlib import Path
import json
import logging as lg
import importlib

import jsonschema

import fvc.df.schema as schema
from fvc.df.util import JsonlinesIO, fetch_input_file

import fvc.df.flightlog as flightlog
import fvc.df.metadata as metadata
import fvc.df.fusion as fusion


MAX_ERRORS = 100


def isValid(input_file: Path):
    with click.progressbar(length=input_file.stat().st_size, label='Validating data') as bar:
        with JsonlinesIO(input_file, 'rt', callback=lambda s: bar.update(s)) as f:
            try:
                metaline = f.read()

                if not metaline:
                    raise UserWarning('Cannon read a metadata line')

                jsonschema.validate(metaline, schema.METADATA)
                content = metaline['content']

                if content not in schema.CONTENT_SCHEMA:
                    raise UserWarning(f'Unknown content type: {content}')

                content_schema = schema.CONTENT_SCHEMA[content]

            except Exception as e:
                lg.error(f'Metadata validation error at line {f.in_line_no()}: {e}')
                return False

            error_count = 0

            for data in f.iterate():
                try:
                    jsonschema.validate(data, content_schema)

                except Exception as e:
                    lg.error(f'Validation error at line {f.in_line_no()}: {e}')
                    error_count += 1

                if error_count >= MAX_ERRORS:
                    lg.error(f'Maximum number of errors reached ({MAX_ERRORS}), stopping')
                    return False

    lg.info('Validation successful')
    return True


@click.command(help='Validate a FVC file against the known schema')
@click.pass_obj
def validate(params):
    input_file = params['input_file']
    valid = isValid(input_file)

    if params['JSON']:
        print(json.dumps({'valid': valid}))


@click.command(help='Convert an external data file to the FVC format')
@click.pass_obj
@click.option(
    '--output-file', help='Output file',
    type=Path, required=False
)
@click.option(
    '--external-format', help='External data format',
    type=click.Choice(['courageous', 'csgroup', 'nmea', 'senhive', 'safirmqtt']),
    required=True
)
@click.option(
    '--base-date',
    help='A base date should be given manually for formats without date info in timestamps',
    type=click.DateTime(['%d %b %Y', '%Y-%m-%d']),
    required=False
)
@click.option(
    '--egm',
    help='Custom EGM geoid data file (*.pgm). Default: egm96-5.pgm',
    type=Path, required=False
)
@metadata.metadata_args
def convert(params, output_file, external_format, egm, base_date, **kwargs):
    input_file = params['input_file']
    params['output_file'] = output_file if output_file else Path(str(input_file) + '.fvc')
    params['external_format'] = external_format
    params['EGM'] = egm
    params['base_date'] = base_date
    metadata.add_metadata_params(params, **kwargs)

    ext_format_mod = importlib.import_module(f'fvc.df.{external_format}')
    convert_fun = getattr(ext_format_mod, 'convert_to_fvc')
    output_file = params['output_file']
    meta = metadata.initial_metadata(params)

    with JsonlinesIO(output_file, 'wt') as io:
        convert_fun(params, meta, input_file, io)

    lg.info(f'Conversion complete, output written to {output_file}')


@click.command(help='Calculate statistics for a FVC data file')
@click.pass_obj
def stats(params):
    input_file = params['input_file']

    with JsonlinesIO(input_file, 'rt') as io:
        flightlog.stats(params, io)


@click.command(help='Just download and cache external data')
def fetch():
    pass


DESCRIPTION = '''
Data file conversion and manipulation tool

Notes:

    For EGM geoid data download, visit:
    https://geographiclib.sourceforge.io/C++/doc/geoid.html#geoidinst

    To set a default cache directory, use the FVC_CACHE environment variable
'''


@click.group(help=DESCRIPTION)
@click.pass_obj
@click.option(
    '--input-file', help='Input file or S3 URI',
    type=str, required=True
)
@click.option(
    '--cache-dir', help='Directory for caching external data',
    type=Path, envvar='FVC_CACHE', required=False
)
def df(params, input_file, cache_dir):
    params['cache_dir'] = cache_dir
    params['input_file'] = fetch_input_file(params, input_file)


df.add_command(convert)
df.add_command(validate)
df.add_command(stats)
df.add_command(fetch)
df.add_command(fusion.fusion)
