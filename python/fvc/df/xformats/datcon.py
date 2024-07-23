from pathlib import Path
import csv
import pyparsing as pp

from fvc.df.util import JsonlinesIO


def grammar():
    lp = pp.Literal('(')
    rp = pp.Literal(')')
    word = pp.Word(pp.alphas)
    comment = pp.Suppress(lp + pp.OneOrMore(word) + rp)
    column = word + pp.Optional(comment)
    return pp.OneOrMore(column)


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):

    with input_path.open('rt') as input:
        header = input.readline()

        if not header:
            return

        columns = grammar().parse_string(header)
        reader = csv.DictReader(input, fieldnames=columns, delimiter=' ')  # type: ignore
        metadata.update({'content': 'flightlog', 'source': 'artlog'})
        output.write(metadata)

        for row in reader:
            assert row['TZ'] == 'UTC'

            record = {
                'time': {
                    'unix': int(row['TS'])
                },
                'uaid': {
                    'int': row['GUID'] if row['GUID'] != 'N/A' else row['ID']
                },
                'pos': {
                    'loc': {
                        'lat': float(row['Latitude']),
                        'lon': float(row['Longitude']),
                        'alt': float(row['Altitude'])
                    }
                }
            }

            output.write(record)
