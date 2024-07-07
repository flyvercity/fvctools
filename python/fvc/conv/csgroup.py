from pathlib import Path
import csv

from fvc.conv.conv_util import JsonlinesIO


def convert_to_fvc(args, input_file: Path, output: JsonlinesIO):
    reader = csv.DictReader(input_file.open())

    metadata = {
        'content': 'flightlog',
        'source': 'csgroup',
        'origin': str(input_file.name),
    }

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
