import sys
from pathlib import Path
import logging as lg
import importlib
import tomllib
import traceback
from typing import cast

import click
import jsonschema
from rich.progress import Progress

from fvc.tools.utils import json_print
import fvc.tools.df.schema as schema
import fvc.tools.df.utils as u

import fvc.tools.df.flightlog as flightlog
import fvc.tools.df.metadata as metadata
import fvc.tools.df.fusion as fusion


MAX_ERRORS = 100


def isValid(input_path: Path):
    file_size = input_path.stat().st_size

    with Progress(transient=True) as progress:
        task = progress.add_task('Validating data', total=file_size)

        with u.JsonlinesIO(input_path, 'r', callback=lambda s: progress.update(task, advance=s)) as f:
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

EPILOG = '''
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
@click.option(
    '--in', 'input', required=False
)
@click.option(
    '--suffix', help='Suffix substitution for input files',
    type=str, required=False
)
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


@df.command(name='help', help='Show help for a specific format')
@click.argument('x_format', type=str, required=True)
def format_help(x_format: str):
    ext_format_mod = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')

    help_text = getattr(ext_format_mod, 'module_help', None)

    if help_text:
        print(help_text())
    else:
        lg.error(f'No help text found for {x_format}')


def convert(params, output_path: Path):
    input_path = params['input'].fetch()

    try:
        params['output_path'] = output_path

        # NB: support for 'crawl' file syntax
        x_format = params.get('x-format') or params.get('x_format')

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


@df.command()
@click.pass_obj
@click.option(
    '--target', help='Target content type',
    type=click.Choice(['flightlog', 'radarlog']), default='flightlog'
)
@click.option(
    '--custom',
    help='Custom parameters for the conversion, use "fvc.df help <x_format>" for details',
    type=str,
    multiple=True,
    required=False
)
@click.argument('x_format', type=str, required=True)
@click.argument('output-file', type=Path, required=False)
@metadata.metadata_args
def convert_command(params, output_file, **kwargs):
    '''Convert an external data file to the FVC format

    \b
    Available formats:
        - agentfly
        - artlog
        - courageous
        - datcon
        - gnettrack
        - nmea
        - robinradar
        - safirmqtt
        - senhive
    '''

    params.update(kwargs)
    input_path = params['input'].fetch()
    output_path = output_file if output_file else input_path.with_suffix('.fvc')
    convert(params, output_path)


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
@click.argument('x_format', type=str, required=True)
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
@click.option('--validate', help='Validate files after conversion', is_flag=True)
def crawl(params, force, validate):
    input_dir = params['input'].as_dir()

    errors = []

    for toml_file in input_dir.glob('**/fvc.df.toml'):
        lg.info(f'Found DF local config {toml_file}')
        crawl_config = tomllib.loads(toml_file.read_text())
        lg.debug(f'Crawl config: {crawl_config}')

        if convert_task := crawl_config.get('convert'):
            for file_glob in convert_task:
                file_def = convert_task[file_glob]
                params.update(file_def)

                if 'x-format' not in file_def:
                    raise UserWarning(f'x-format is required for {file_glob}')
                else:
                    x_format = file_def['x-format']

                if 'target' not in file_def:
                    file_def['target'] = 'flightlog'

                target = file_def['target']
                task_dir = toml_file.parent

                for in_file_path in task_dir.glob(file_glob):
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

                            params['input'] = u.Input(params, in_file_path)
                            convert(params, output_path)

                            if validate:
                                lg.info(f'Validating {output_path.name}')

                                if not isValid(output_path):
                                    errors.append(f'Validation failed for {output_path}')

                        except Exception as e:
                            if params['verbose']:
                                traceback.print_exc(file=sys.stderr)

                            errors.append(f'Error converting {in_file_path}: {e}')
                    else:
                        lg.info(f'Output file {output_path.name} exists, skipping')

    if errors:
        lg.error(f'{len(errors)} errors occurred')

        for error in errors:
            lg.error(error)
    else:
        lg.info('There were no errors')


@df.command(help='Upgrade a FVC file to the latest schema (volatile code)')
@click.argument('infile', type=Path, required=True)
def upgrade(infile):
    infile = Path(infile)
    outfile = infile.with_suffix('.fvc')

    with Progress(transient=True) as progress:
        read_task = progress.add_task('Reading...', total=infile.stat().st_size)
        write_task = progress.add_task('Writing...', total=infile.stat().st_size)

        with (
            u.JsonlinesIO(
                infile, 'r',
                callback=lambda s: progress.update(read_task, advance=s)
            ) as infile,
            u.JsonlinesIO(
                outfile, 'w',
                callback=lambda s: progress.update(write_task, advance=s)
            ) as outfile
        ):
            metaline = infile.read()
            outfile.write(metaline)

            for record in infile.iterate():
                cell = record.get('cellsig')

                if not cell:
                    continue

                cell = cast(dict, cell)

                if 'RSRP_4G' in cell:
                    del cell['RSRP_4G']

                if 'RSRP_5G' in cell:
                    del cell['RSRP_5G']

                if 'RSRQ_4G' in cell:
                    del cell['RSRQ_4G']

                if 'RSRQ_5G' in cell:
                    del cell['RSRQ_5G']

                cell['radio'] = '4GLTE'
                outfile.write(record)


df.add_command(fusion.fusion)
