from pathlib import Path
from datetime import datetime, UTC
import logging as lg
import statistics

import pynmea2

from fvc.df.util import JsonlinesIO, JSON


def iterate_nmea_file(input_path: Path):
    with input_path.open() as f:
        while line := f.readline():
            try:
                message = pynmea2.parse(line)

                yield message

            except ValueError as e:
                lg.warning(f'Unable to parse line ({line}) with error: {e}')


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    base_date = params.get('base_date')  # type: datetime

    if not base_date:
        raise UserWarning("This format requires the date to be set manually with '--base-date'")

    lg.debug(f'Using base date: {base_date}')
    metadata.update({'content': 'flightlog', 'source': 'nmea'})
    output.write(metadata)

    for message in iterate_nmea_file(input_path):
        if not isinstance(message, pynmea2.GGA):
            continue

        timestamp = datetime.combine(base_date, message.timestamp, tzinfo=UTC)  # type: ignore

        record = {
            'time': {'unix': int(timestamp.timestamp()*1000)},
            'pos': {
                'loc': {
                    'lat': message.latitude,
                    'lon': message.longitude,
                    # TODO: handle feet
                    'alt': message.altitude + float(message.geo_sep)  # type: ignore
                }
            }
        }

        output.write(record)


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
