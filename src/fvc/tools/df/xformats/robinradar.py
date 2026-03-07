import logging as lg
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TextIO

import fvc.tools.utils as u
from fvc.tools.df.utils import JsonlinesIO


def iterate_robin(f: TextIO):
    line_no = 0

    while True:
        line = f.readline()
        line_no += 1

        if not line:
            return

        if '<Robin>' in line:
            lines = [line]

            while '</Robin>' not in line:
                if line := f.readline():
                    line_no += 1
                    lines.append(line)
                else:
                    return

            yield (line_no, ''.join(lines))


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    metadata.update({'content': 'flightlog', 'source': 'robinradar'})
    output.write(metadata)

    with input_path.open('rt') as f:
        block_no = 0

        for line_no, block in iterate_robin(f):
            block_no += 1

            try:
                root = ET.fromstring(block)

                for track in root.findall('.//Track'):
                    track_id = track.get('id')

                    if track_id is None:
                        continue

                    record = {'uid': {'int': track_id}}

                    timestamp_elem = track.find('Timestamp')
                    if timestamp_elem is not None and timestamp_elem.text:
                        record['time'] = {'unix': u.datestring_to_ts(timestamp_elem.text)}
                    else:
                        raise ValueError('Incomplete timestamp record')

                    pos_elem = track.find('Position')
                    if pos_elem is not None:
                        lat_elem = pos_elem.find('Latitude')
                        lon_elem = pos_elem.find('Longitude')
                        alt_elem = pos_elem.find('Altitude')

                        if lat_elem is not None and lat_elem.text and \
                           lon_elem is not None and lon_elem.text and \
                           alt_elem is not None and alt_elem.text:
                            record['pos'] = {
                                'loc': {
                                    'lat': float(lat_elem.text),
                                    'lon': float(lon_elem.text),
                                    'alt': float(alt_elem.text)
                                }
                            }
                        else:
                            raise ValueError('Incomplete position record')
                    else:
                        raise ValueError('Incomplete position record')

                    output.write(record)

            except Exception as e:
                lg.warning(
                    f'Error parsing block {block_no} line {line_no}: {e}'
                )
