from pathlib import Path
from datetime import datetime, UTC
import logging as lg

import pynmea2

from fvc.conv.conv_util import JsonlinesIO


def convert_to_fvc(args, input_file: Path, output: JsonlinesIO):
    base_date = args.base_date  # type: datetime

    if not base_date:
        raise UserWarning("This format requires the date to be set manually with '--base-date'")

    lg.debug(f'Using base date: {base_date}')

    metadata = {
        'content': 'flightlog',
        'source': 'nmea',
        'origin': str(input_file.name),
    }

    output.write(metadata)

    with input_file.open() as f:
        while line := f.readline():
            try:
                message = pynmea2.parse(line)

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

            except ValueError as e:
                lg.warning(f'Unable to parse line ({line}) with error: {e}')
