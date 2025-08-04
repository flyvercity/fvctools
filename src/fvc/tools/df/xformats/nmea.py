'''
NMEA log format

Custom parameters:
    - base-date=<datestring> is required for this format
'''

from pathlib import Path
from datetime import datetime, UTC
import logging as lg
import statistics

import pynmea2
from dateutil.parser import parse as dateparse

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.utils import JSON


def module_help():
    return '- base-date=<datestring> is required for this format'


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    base_date = None

    for custom in params.get('custom', []):
        if custom.startswith('base-date='):
            base_date = custom.split('=')[1]
            break

    if isinstance(base_date, str):
        base_date = dateparse(base_date)

    if not base_date:
        raise UserWarning(
            'This format requires the date to be set manually with "base-date" custom parameter'
        )

    lg.debug(f'Using base date: {base_date}')

    metadata.update({
        'content': 'flightlog',
        'source': 'nmea',
        'base-date': base_date.date().isoformat()
    })

    output.write(metadata)

    for message in iterate_nmea_file(input_path):
        if not isinstance(message, pynmea2.GGA):
            continue

        timestamp = datetime.combine(base_date, message.timestamp, tzinfo=UTC)  # type: ignore

        if not message.geo_sep:
            continue

        # TODO: handle feet
        alt = message.altitude + float(message.geo_sep)  # type: ignore

        record = {
            'time': {'unix': int(timestamp.timestamp() * 1000)},
            'pos': {
                'loc': {
                    'lat': message.latitude,
                    'lon': message.longitude,
                    'alt': alt
                }
            }
        }

        output.write(record)


def iterate_nmea_file(input_path: Path):
    with input_path.open() as f:
        while line := f.readline():
            try:
                message = pynmea2.parse(line)

                yield message

            except ValueError as e:
                lg.warning(f'Unable to parse line ({line}) with error: {e}')


def extract_sensor_data(params, sensor_source: Path) -> JSON:
    lg.info(f'Extracting sensor data from {sensor_source}')

    def iterate():
        for message in iterate_nmea_file(sensor_source):
            if isinstance(message, pynmea2.GGA):
                yield (message.latitude, message.longitude, message.altitude)

    (latitudes, longitudes, altitudes) = zip(*iterate())

    return {
        'loc': {
            'lat': statistics.median(latitudes),
            'lon': statistics.median(longitudes),
            'alt': statistics.median(altitudes)
        }
    }
