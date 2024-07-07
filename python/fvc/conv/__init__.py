from pathlib import Path
import json
import jsonschema


import fvc.conv.schema as schema


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
            print(f'Metadata validation error at line {line_no}: {e}')
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
                print(f'Validation error at line {line_no}: {line}: {e}')
                error_count += 1

            if error_count >= MAX_ERRORS:
                print(f'Maximum number of errors reached ({MAX_ERRORS}), stopping')
                return False

    return True


def validate(args):
    input_file = args.input_file  # type: Path
    valid = isValid(input_file)

    if args.json:
        print(json.dumps({'valid': valid}))


COMMANDS = {
    'validate': validate
}

DESCRIPTION = '''
Subcommands:
    validate: Validate a FVC file against the known CUE schema
'''


def add_argparser(name, subparsers):
    parser = subparsers.add_parser(
        name, help='Data management and conversion tool',
        description=DESCRIPTION
    )

    parser.add_argument('command', help='Converter command', choices=COMMANDS.keys())
    parser.add_argument('--input-file', help='Input file', type=Path)


def main(args):
    COMMANDS[args.command](args)
