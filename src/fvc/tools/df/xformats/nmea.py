"""
NMEA log format

Custom parameters:
    - base-date=<datestring> is required for this format
"""

import array
import logging as lg
import statistics
from datetime import UTC, datetime
from pathlib import Path

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

    metadata.update(
        {
            'content': 'flightlog',
            'source': 'nmea',
            'base-date': base_date.date().isoformat(),
        }
    )

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
                    'alt': alt,
                }
            },
        }

        output.write(record)


def iterate_nmea_file(input_path: Path, strict: bool = False):
    with input_path.open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                yield pynmea2.parse(line)

            except (pynmea2.ParseError, ValueError) as e:
                if strict:
                    raise ValueError(
                        f'Unable to parse line {line_no} ({line}) with error: {e}'
                    ) from e

                lg.warning(f'Unable to parse line {line_no} ({line}) with error: {e}')


def extract_sensor_data(params, sensor_source: Path) -> JSON:
    lg.info(f'Extracting sensor data from {sensor_source}')

    latitudes = array.array('d')
    longitudes = array.array('d')
    altitudes = array.array('d')

    for message in iterate_nmea_file(sensor_source):
        if isinstance(message, pynmea2.GGA):
            latitudes.append(message.latitude)
            longitudes.append(message.longitude)
            altitudes.append(message.altitude)

    if not latitudes:
        raise ValueError(f'No GGA messages found in {sensor_source}')

    return {
        'loc': {
            'lat': statistics.median(latitudes),
            'lon': statistics.median(longitudes),
            'alt': statistics.median(altitudes),
        }
    }
