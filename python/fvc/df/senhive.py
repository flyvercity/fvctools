from pathlib import Path
import csv
import logging as lg

from datetime import UTC
from dateutil.parser import isoparse

from fvc.df.util import JsonlinesIO


def convert_to_fvc(params, metadata, input_file: Path, output: JsonlinesIO):
    reader = csv.DictReader(input_file.open(), delimiter=';')
    row_no = 1

    metadata.update({
        'content': 'flightlog',
        'source': 'senhive'
    })

    output.write(metadata)

    for row in reader:
        row_no += 1
        date = isoparse(row["'timestamp'"]).replace(tzinfo=UTC)
        timestamp = int(date.timestamp() * 1000)
        lat = row.get("'vehicle_location_lat'")
        lon = row["'vehicle_location_lon'"]
        alt = row["'altitude_gps (m)'"]

        if not lat or not lon or not alt:
            lg.warning(f'Invalid data at line {row_no}')
            continue

        record = {
            'time': {'unix': timestamp},
            'uaid': {
                'int': row["'track_id'"],
                'serial': row["'vehicle_serial_number'"]
            },
            'pos': {
                'loc': {
                    'lat': float(lat),
                    'lon': float(lon),
                    'alt': float(alt)
                }
            }
        }

        output.write(record)
