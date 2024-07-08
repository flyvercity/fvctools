import json
from pathlib import Path
import logging as lg

from toolz.dicttoolz import keyfilter
from pygeodesy.geoids import GeoidPGM

from fvc.df.util import JsonlinesIO


def amsl_to_ellipsoidal(geoid, lat, lon, amsl_height):
    # Initialize the Geoid model using EGM96 with WGS-84 datum
    geoid_height = geoid.height(lat, lon)
    ellipsoidal_height = amsl_height + geoid_height
    return ellipsoidal_height


def build_geo_position(pos, geoid):
    lat = pos['lat']
    lon = pos['lon']
    amsl = pos['height_amsl']
    alt = amsl_to_ellipsoidal(geoid, lat, lon, amsl)

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


def convert_to_fvc(args, metadata, input_file: Path, output: JsonlinesIO):
    pgm_path = Path(__file__).parent / 'egm96-5.pgm'

    if args.egm:
        pgm_path = Path(args.egm)

    lg.debug(f'Using geoid model: {pgm_path.absolute()}')

    geoid = GeoidPGM(pgm_path)
    data = json.loads(input_file.read_text())

    metadata.update({
        'content': 'flightlog',
        'source': 'courageous',
        'origin': str(input_file.name),
        'geoid': pgm_path.name
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
