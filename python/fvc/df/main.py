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


MAX_ERRORS = 100


def isValid(input_file: Path):
    line_no = 0

    with input_file.open('rt', encoding='utf-8', newline=None) as f:
        try:
            metaline = f.readline()
            line_no += 1

            metadata = json.loads(metaline)
            jsonschema.validate(metadata, schema.METADATA)
            content = metadata['content']

            if content not in schema.CONTENT_SCHEMA:
                raise UserWarning(f'Unknown content type: {content}')

            content_schema = schema.CONTENT_SCHEMA[metadata['content']]

        except Exception as e:
            lg.error(f'Metadata validation error at line {line_no}: {e}')
            return False

        error_count = 0

        while True:
            line = f.readline()
            line_no += 1

            if not line.strip():
                break

            try:
                data = json.loads(line)
                jsonschema.validate(data, content_schema)

            except Exception as e:
                lg.error(f'Validation error at line {line_no}: {line}: {e}')
                error_count += 1

            if error_count >= MAX_ERRORS:
                lg.error(f'Maximum number of errors reached ({MAX_ERRORS}), stopping')
                return False

    lg.info('Validation successful')
    return True


@click.command(help='Validate a FVC file against the known schema')
@click.pass_context
def validate(ctx):
    input_file = ctx.obj['input_file']
    valid = isValid(input_file)

    if ctx.obj['JSON']:
        print(json.dumps({'valid': valid}))


@click.command(help='Convert an external data file to the FVC format')
@click.pass_context
@click.option(
    '--output-file', help='Output file',
    type=Path, required=False
)
@click.option(
    '--external-format', help='External data format',
    type=click.Choice(['courageous', 'csgroup', 'nmea', 'senhive']),
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
def convert(ctx, output_file, external_format, egm, base_date, **kwargs):
    input_file = ctx.obj['input_file']
    ctx.obj['output_file'] = output_file if output_file else Path(str(input_file) + '.fvc')
    ctx.obj['external_format'] = external_format
    ctx.obj['EGM'] = egm
    ctx.obj['base_date'] = base_date
    metadata.add_metadata_params(ctx.obj, **kwargs)

    ext_format_mod = importlib.import_module(f'fvc.df.{external_format}')
    convert_fun = getattr(ext_format_mod, 'convert_to_fvc')
    output_file = ctx.obj['output_file']
    meta = metadata.initial_metadata(ctx.obj)

    with JsonlinesIO(output_file, 'wt') as io:
        convert_fun(ctx.obj, meta, input_file, io)

    lg.info(f'Conversion complete, output written to {output_file}')


@click.command(help='Calculate statistics for a FVC data file')
@click.pass_context
def stats(ctx):
    input_file = ctx.obj['input_file']

    with JsonlinesIO(input_file, 'rt') as io:
        flightlog.stats(ctx.obj, io)


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
@click.pass_context
@click.option(
    '--input-file', help='Input file or S3 URI',
    type=str, required=True
)
@click.option(
    '--cache-dir', help='Directory for caching external data',
    type=Path, envvar='FVC_CACHE', required=False
)
def df(ctx, input_file, cache_dir):
    ctx.ensure_object(dict)
    ctx.obj['cache_dir'] = cache_dir
    ctx.obj['input_file'] = fetch_input_file(ctx.obj, input_file)


df.add_command(convert)
df.add_command(validate)
df.add_command(stats)
df.add_command(fetch)
