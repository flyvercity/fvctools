from pathlib import Path
import csv

from fvc.tools.df.util import JsonlinesIO


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    with input_path.open('rt') as input:
        reader = csv.DictReader(input)

        metadata.update({
            'content': 'flightlog',
            'source': 'csgroup'
        })

        output.write(metadata)

        for row in reader:
            event = row.get('event_type')

            if event != 'TRACK':
                continue

            timestamp = row['datetime_ms']
            track_id = row['track_id']
            lat = row['latitude']
            lon = row['longitude']
            alt = row['altitude']

            uaid = {
                'int': track_id
            }

            time = {
                'unix': int(timestamp)
            }

            position = {
                'loc': {
                    'lat': float(lat),
                    'lon': float(lon),
                    'alt': float(alt)
                }
            }

            record = {
                'time': time,
                'uaid': uaid,
                'pos': position
            }

            output.write(record)
