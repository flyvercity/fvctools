import json
from pathlib import Path

from toolz.dicttoolz import keyfilter

from fvc.conv.conv_util import JsonlinesIO


def amsl_to_alt(amsl):
    # TODO: Convert AMSL to altitude
    return amsl


def convert_to_fvc(input_file: Path, output: JsonlinesIO):
    data = json.loads(input_file.read_text())

    metadata = {
        'content': 'flightlog',
        'source': 'bluehalo',
        'origin': str(input_file.absolute())
    }

    metakeys = ['system_name', 'version']
    metadata.update(keyfilter(lambda k: k in metakeys, data))
    output.write(metadata)

    entries = []

    for track in data.get('tracks', []):
        uaid = {
            'system': 'internal',
            'value': f"{track['name']}-{track['uas_id']}"
        }

        def record_to_entry(record):
            timestamp = {
                'unix': record['time']
            }

            loc = record['location']['c']
            lat = loc['lat']
            lon = loc['lon']
            alt = amsl_to_alt(loc['height_amsl'])

            position = {
                'loc': {
                    'lat': lat,
                    'lon': lon,
                    'alt': alt
                }
            }

            return {
                'time': timestamp,
                'uaid': uaid,
                'pos': position
            }

        entries.extend(map(record_to_entry, track['records']))

    entries.sort(key=lambda e: e['time']['unix'])

    for entry in entries:
        output.write(entry)
