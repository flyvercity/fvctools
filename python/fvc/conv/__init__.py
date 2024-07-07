from pathlib import Path
import json
import jsonschema
import logging as lg


import fvc.conv.schema as schema
import fvc.conv.bluehalo as bluehalo
from fvc.conv.conv_util import JsonlinesIO, EndOfInput


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


def validate(args):
    input_file = args.input_file  # type: Path
    valid = isValid(input_file)

    if args.json:
        print(json.dumps({'valid': valid}))


TOFVC_CONVERTERS = {
    'bluehalo': bluehalo.convert_to_fvc
}


def convert(args):
    if args.external_format not in TOFVC_CONVERTERS:
        lg.error(f'Unknown external format: {args.external_format}')
        return

    try:
        with JsonlinesIO(args.output_file, 'wt') as io:
            TOFVC_CONVERTERS[args.external_format](args.input_file, io)

    except EndOfInput:
        lg.info('Conversion complete')
    except Exception as e:
        lg.error(f'Error during conversion: {e}')

    if not isValid(args.output_file):
        lg.error('Generated file does not comply to the known schema')


COMMANDS = {
    'validate': validate,
    'convert': convert
}

DESCRIPTION = '''
Subcommands:
    validate: Validate a FVC file against the known CUE schema
    convert: Convert an external data file to FVC format
'''


def add_argparser(name, subparsers):
    parser = subparsers.add_parser(
        name, help='Data management and conversion tool',
        description=DESCRIPTION
    )

    parser.add_argument('command', help='Converter command', choices=COMMANDS.keys())
    parser.add_argument('--input-file', help='Input file', type=Path)
    parser.add_argument('--output-file', help='Output file', type=Path)

    parser.add_argument(
        '--external-format', help='External data format',
        choices=['bluehalo']
    )


def main(args):
    COMMANDS[args.command](args)
