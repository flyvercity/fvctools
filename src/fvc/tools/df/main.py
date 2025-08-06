from pathlib import Path
import logging as lg
import importlib
from typing import Callable

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


def isValid(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
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
