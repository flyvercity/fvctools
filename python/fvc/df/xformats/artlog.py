from pathlib import Path
import csv

from fvc.df.util import JsonlinesIO


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    reader = csv.DictReader(input_path.open(), delimiter=' ')

    metadata.update({
        'content': 'flightlog',
        'source': 'artlog'
    })

    output.write(metadata)

    for row in reader:
        assert row['TimeZone'] == 'UTC'

        record = {
            'time': {
                'unix': int(row['Timestamp_nsec']) // int(1_000_000)
            },
            'uaid': {
                'int': row['TrackUUID']
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
