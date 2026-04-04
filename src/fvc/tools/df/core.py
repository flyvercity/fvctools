import importlib
from pathlib import Path
from typing import Callable, Optional, TypedDict

import jsonschema

import fvc.tools.df.metadata as metadata
import fvc.tools.df.schema as schema
import fvc.tools.df.utils as dfu
from fvc.tools.df.utils import lg

MAX_ERRORS = 100


class DFParams(TypedDict):
    input_path: Path
    output_path: Path
    x_format: str
    force: bool = False
    validate: bool = False
    custom: Optional[str]


def convert(
    params: DFParams,
    callback: Callable[[int], None] | None = None,
):
    """
    Convert a file from an external format to FVC format.

    Args:
        params: Parameters for the conversion:
            - `input_path`: Input file path
            - `output_path`: Output file path
            - `x_format`: External format
        callback: Callback function to update the progress
            - `bytes_read`: Number of bytes read
    """

    input_path = params['input_path']
    output_path = params['output_path']

    if input_path.absolute() == output_path.absolute():
        raise UserWarning('Input and output paths are the same')

    try:
        x_format = params['x_format']

        lg.debug(f'Using external format module: {x_format}')

        ext_format_mod = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')

        lg.debug('Imported external format function')

        convert_fun = getattr(ext_format_mod, 'convert_to_fvc')
        meta = metadata.create_metadata(input_path.name, params)

        with dfu.JsonlinesIO(output_path, 'w') as io:
            convert_fun(params, meta, input_path, io)

    except ModuleNotFoundError as e:
        lg.error(f'Error importing external format module: {e}')
        raise UserWarning(f'Unknown external format: {params["x_format"]}')


def validate(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
    with dfu.JsonlinesIO(input_path, 'r', callback=callback) as f:
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

        try:
            # ⚡ Bolt: Create the validator once to avoid recompilation overhead for each record.
            # This significantly improves performance for large files.
            cls = jsonschema.validators.validator_for(content_schema)
            cls.check_schema(content_schema)
            validator = cls(content_schema)

        except Exception as e:
            lg.error(f'Schema error: {e}')
            return False

        for data in f.iterate():
            try:
                validator.validate(data)

            except Exception as e:
                lg.error(f'Validation error at line {f.in_line_no()}: {e}')
                error_count += 1

            if error_count >= MAX_ERRORS:
                lg.error(f'Maximum number of errors reached ({MAX_ERRORS}), stopping')

                return False

    success = error_count == 0
    return success


def export(params: DFParams):
    """Parameters:
    - input: input file path
    - output_path: output file path
    - x_format: external format
    """

    output_path = params['output_path']
    x_format = params['x_format']

    lg.debug(f'Using external format module: {x_format}')

    export_module = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')
    export_fun = getattr(export_module, 'export_from_fvc')
    real_output = export_fun(params, output_path)

    lg.info(f'Export complete, output written to {real_output}')


