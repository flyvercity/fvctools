import sys
from pathlib import Path
import logging as lg
import importlib
import sys
import tomllib
import traceback
from datetime import datetime

import click
import jsonschema

from fvc.tools.util import json_print
import fvc.tools.df.schema as schema
import fvc.tools.df.util as u

import fvc.tools.df.flightlog as flightlog
import fvc.tools.df.metadata as metadata
import fvc.tools.df.fusion as fusion


MAX_ERRORS = 100


def isValid(input_path: Path):
    with click.progressbar(
        length=input_path.stat().st_size, 
        label='Validating data',
        file=sys.stderr
    ) as bar:
        with u.JsonlinesIO(input_path, 'r', callback=lambda s: bar.update(s)) as f:
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

    success = error_count == 0
    lg.info(f'Validation {"succeeded" if success else "failed"}')
    return success


DESCRIPTION = 'Data file conversion and manipulation tool'

EPILOG='''
Notes:

    For EGM geoid data download, visit:
    https://geographiclib.sourceforge.io/C++/doc/geoid.html#geoidinst

    To set a default cache directory, use the FVC_CACHE environment variable.

    From examples of 'fvc.df.toml' files, see 'examples/df' directory in the source code.
'''


@click.group(help=DESCRIPTION, epilog=EPILOG)
@click.pass_obj
@click.option(
    '--cache-dir', help='Directory for caching external data',
    type=Path, envvar='FVC_CACHE', required=False
)
@click.argument('input', required=True)
def df(params, input, **kwargs):
    params.update(kwargs)
    params['input'] = u.Input(params, input)


@df.command(help='Validate a FVC file against the known schema')
@click.pass_obj
def validate(params):
    input_path = params['input'].fetch()
    valid = isValid(input_path)

    if params['JSON']:
        json_print(params, {'valid': valid})


def do_convert(params, input_path: Path, output_path: Path):
    try:
        params['output_path'] = output_path

        x_format = params['x_format']

        lg.debug(f'Using external format module: {x_format}')
        ext_format_mod = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')
        lg.debug('Imported external format function')
        convert_fun = getattr(ext_format_mod, 'convert_to_fvc')
        meta = metadata.initial_metadata(params)

        with u.JsonlinesIO(output_path, 'w') as io:
            convert_fun(params, meta, input_path, io)

        lg.info(f'Conversion complete, output written to {output_path}')
    except ModuleNotFoundError as e:
        lg.error(f'Error importing external format module: {e}')
        raise UserWarning(f'Unknown external format: {params["x_format"]}')


@df.command(help='Convert an external data file to the FVC format')
@click.pass_obj
@click.option(
    '--target', help='Target content type',
    type=click.Choice(['flightlog', 'radarlog']), default='flightlog'
)
@click.option(
    '--base-date',
    help='A base date should be given manually for formats without date info in timestamps',
    type=click.DateTime(['%d %b %Y', '%Y-%m-%d']),
    required=False
)
@click.argument('x_format', type=str, required=True)
@click.argument('output-file', type=Path, required=False)
@metadata.metadata_args
def convert(params, x_format, output_file, **kwargs):
    params['x_format'] = x_format
    params.update(kwargs)
    input_path = params['input'].fetch()
    output_path = output_file if output_file else input_path.with_suffix('.fvc')
    do_convert(params, input_path, output_path)


@df.command(help='Calculate statistics for a FVC data file')
@click.pass_obj
def stats(params):
    input_path = params['input'].fetch()

    with u.JsonlinesIO(input_path, 'r') as io:
        flightlog.stats(params, io)


@df.command(help='Just download and cache external data')
@click.pass_obj
def fetch(params):
    params['input'].fetch()
    
    if not params['JSON']:
        lg.info('This file is available in the cache')
    else:
        path = str(params['input'].fetch().resolve())
        json_print(params, {'path': path})


@df.command(help='Convert data to an external format')
@click.pass_obj
@click.option(
    '--x-format', help='External data format',
    type=click.Choice(['geojson', 'kml']), required=True
)
@click.option('--with-cellular', help='Require cellular signal data', is_flag=True)
@click.argument('output-file', type=Path, required=False)
def export(params, x_format, output_file, **kwargs):
    params.update(kwargs)
    export_module = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')
    export_fun = getattr(export_module, 'export_from_fvc')
    real_output = export_fun(params, output_file)
    lg.info(f'Export complete, output written to {real_output}')


@df.command(help='Scan for fvc.df.toml files and execute tasks')
@click.pass_obj
@click.option('--force', help='Reconvert files even if they exist', is_flag=True)
def crawl(params, force):
    input_dir = params['input'].as_dir()

    for toml_file in input_dir.glob('**/fvc.df.toml'):
        lg.info(f'Found DF local config {toml_file}')
        crawl_config = tomllib.loads(toml_file.read_text())

        if convert_task := crawl_config.get('convert'):
            for file_def in convert_task:
                x_format = convert_task[file_def]['x-format']
                target = convert_task[file_def].get('target', 'flightlog')

                params.update(convert_task[file_def].get('extra', {}))
                params.update({'x_format': x_format, 'target': target})

                task_dir = toml_file.parent

                for in_file_path in task_dir.glob(file_def):
                    if in_file_path.is_dir():
                        lg.info(f'Found directory {in_file_path}, skipping')
                        continue

                    if in_file_path.name == 'fvc.df.toml':
                        continue

                    if in_file_path.suffix == '.fvc':
                        lg.info(f'File {in_file_path.name} is already in FVC format, skipping')
                        continue

                    output_path = in_file_path.with_suffix('.fvc')
                    
                    if not output_path.exists() or force:
                        try:
                            lg.info(
                                f'Converting {in_file_path.name} from {x_format} to {target}'
                            )

                            do_convert(params, in_file_path, output_path)
                        except Exception as e:
                            if params['verbose']:
                                traceback.print_exc(file=sys.stderr)

                            lg.error(f'Error converting {in_file_path}: {e}')
                    else:
                        lg.info(f'Output file {output_path.name} exists, skipping')


df.add_command(fusion.fusion)
