from pathlib import Path
import logging as lg
import importlib
import tomllib
from typing import Callable
import traceback
import sys

import jsonschema

import fvc.tools.df.schema as schema
import fvc.tools.df.utils as u

import fvc.tools.df.metadata as metadata


MAX_ERRORS = 100


def convert(params):
    ''' Parameters:
        - input: input file path
        - output_path: output file path
        - x_format: external format
    '''

    output_path = params['output_path']
    input_path = params['input'].fetch()

    try:

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


def validate(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
    with u.JsonlinesIO(input_path, 'r', callback=callback) as f:
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
    return success


def export(params):
    ''' Parameters:
        - input: input file path
        - output_path: output file path
        - x_format: external format
    '''

    output_path = params['output_path']
    x_format = params.get('x_format')

    lg.debug(f'Using external format module: {x_format}')
    export_module = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')
    export_fun = getattr(export_module, 'export_from_fvc')
    real_output = export_fun(params, output_path)
    lg.info(f'Export complete, output written to {real_output}')


def crawl(params):
    ''' Parameters:
        - input: input file path
        - force: force conversion even if output file exists
        - validate: validate output file after conversion
    '''

    input_dir = params['input'].as_dir()
    force = params.get('force')
    validate = params.get('validate')

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
                            params['output_path'] = output_path
                            convert(params)

                            if validate:
                                lg.info(f'Validating {output_path.name}')

                                if not validate(output_path):
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


def upgrade(params, read_callback, write_callback):
    infile = params['input'].fetch()
    outfile = params['output_path']

    with (
        u.JsonlinesIO(
            infile, 'r',
            callback=read_callback
        ) as infile,
        u.JsonlinesIO(
            outfile, 'w',
            callback=write_callback
        ) as outfile
    ):
        for record in infile.iterate():
            ...
            outfile.write(record)
