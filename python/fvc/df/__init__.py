from pathlib import Path
import json
import logging as lg
from argparse import RawTextHelpFormatter
import importlib
import os

import dateutil.parser
import jsonschema
import dateutil

import fvc.df.schema as schema
from fvc.df.util import JsonlinesIO, fetch_input_file

import fvc.df.flightlog as flightlog


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
    input_file = fetch_input_file(args)
    valid = isValid(input_file)

    if args.json:
        print(json.dumps({'valid': valid}))


def convert(args):
    if not (format := args.external_format):
        raise UserWarning('External format not specified')

    format_mod = importlib.import_module(f'fvc.df.{format}')
    convert_fun = getattr(format_mod, 'convert_to_fvc')
    input_file = fetch_input_file(args)
    output_file = args.output_file if args.output_file else Path(str(input_file) + '.fvc')

    with JsonlinesIO(output_file, 'wt') as io:
        convert_fun(args, input_file, io)

    lg.info(f'Conversion complete, output written to {output_file}')


def stats(args):
    input_file = fetch_input_file(args)

    with JsonlinesIO(input_file, 'rt') as io:
        flightlog.stats(args, io)


COMMANDS = {
    'validate': validate,
    'convert': convert,
    'stats': stats
}

DESCRIPTION = '''
Subcommands:
    validate: Validate a FVC file against the known schema
    convert: Convert an external data file to FVC format
    stats: Calculate statistics for a FVC data file

Note:
    For EGM geoid data download, visit:
    https://geographiclib.sourceforge.io/C++/doc/geoid.html#geoidinst
'''


def add_argparser(name, subparsers):
    def dateparam(s):
        return dateutil.parser.parse(s)

    parser = subparsers.add_parser(
        name, help='Data file management and conversion tool',
        description=DESCRIPTION,
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument('command', help='Data file manipulation command', choices=COMMANDS.keys())
    parser.add_argument('--input-file', help='Input file', type=str)
    parser.add_argument('--output-file', help='Output file', type=Path)

    parser.add_argument(
        '--cache-dir', help='Directory for caching external data',
        type=str, default=os.getenv('FVC_CACHE')
    )

    parser.add_argument(
        '--egm',
        help='Custom EGM geoid data file (*.pgm). Default: egm96-5.pgm',
        type=Path
    )

    parser.add_argument(
        '--external-format', help='External data format',
        choices=['courageous', 'csgroup', 'nmea', 'senhive']
    )

    parser.add_argument(
        '--base-date',
        help='Base date should be given manually for formats without date in timestamps',
        type=dateparam
    )


def main(args):
    COMMANDS[args.command](args)
