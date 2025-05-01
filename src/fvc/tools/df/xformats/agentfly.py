
from pathlib import Path
import csv
import logging as lg

from fvc.tools.df.util import JsonlinesIO


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    metadata.update({'content': 'flightlog', 'source': 'agentfly'})
    output.write(metadata)
    with input_path.open('rt') as input:
        reader = csv.DictReader(input)

        for row in reader:
            try:
                record = {
                    'time': {'unix': int(row['#unix_timestamp'])},
                    'uaid': {'int': row['flight_id']},
                    'pos': {
                        'loc': {
                            'lat': float(row['latitude_deg']),
                            'lon': float(row['longitude_deg']),
                            'alt': float(row['altitude_m'])
                        }
                    },
                    'source': row['source_id']
                }

                output.write(record)

            except Exception as e:
                lg.error(f'Error reading record: {e}')
                continue
