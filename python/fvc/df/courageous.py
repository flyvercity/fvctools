import json
from pathlib import Path

from toolz.dicttoolz import keyfilter

import fvc.df.util as u


def build_geo_position(pos, geoid):
    lat = pos['lat']
    lon = pos['lon']
    amsl = pos['height_amsl']
    alt = u.amsl_to_ellipsoidal(geoid, lat, lon, amsl)

    position = {
        'loc': {
            'lat': lat,
            'lon': lon,
            'alt': alt
        }
    }

    return position


def build_polar_position(pos):
    position = {
        'polar': {
            'bear': pos['bearing'],
            'elev': pos['elevation']
        }
    }

    return position


def convert_to_fvc(params, metadata, input_path: Path, output: u.JsonlinesIO):
    geoid = u.load_geoid(params, metadata)
    data = json.loads(input_path.read_text())

    metadata.update({
        'content': 'flightlog',
        'source': 'courageous'
    })

    metakeys = ['system_name', 'version']
    metadata.update(keyfilter(lambda k: k in metakeys, data))
    output.write(metadata)

    entries = []

    for track in data.get('tracks', []):
        track_name = track.get('name', 'unknown')
        track_id = track.get('uas_id', 'noid')

        uaid = {
            'int': f'{track_name}-{track_id}',
        }

        def record_to_entry(record):
            timestamp = {
                'unix': record['time']
            }

            loc = record['location']

            if 't' in loc and loc['t'] == 'Position3d':
                position = build_geo_position(loc['c'], geoid)

            elif 'Position3d' in record['location']:
                position = build_geo_position(loc['Position3d'], geoid)

            elif 't' in loc and loc['t'] == 'BearingElevation':
                position = build_polar_position(loc['c'])

            return {
                'time': timestamp,
                'uaid': uaid,
                'pos': position
            }

        entries.extend(map(record_to_entry, track['records']))

    entries.sort(key=lambda e: e['time']['unix'])

    for entry in entries:
        output.write(entry)
