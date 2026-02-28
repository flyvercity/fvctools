import json
import logging as lg
from pathlib import Path

import fvc.tools.utils as u
from fvc.tools.df.utils import JsonlinesIO


def _build_cartesian_position(loc, geoid):
    if 't' in loc and loc['t'] == 'Position3d':
        pos = loc['c']
    elif 'Position3d' in loc:
        pos = loc['Position3d']
    else:
        lg.warning(f'Unused location format: {loc.get("t")}')
        return None

    lat = pos['lat']
    lon = pos['lon']
    amsl = pos['height_amsl']
    alt = u.amsl_to_ellipsoidal(geoid, lat, lon, amsl)

    return {'loc': {'lat': lat, 'lon': lon, 'alt': alt}}


def _build_polar_position(loc):
    loc_format = loc.get('t')

    if loc_format == 'BearingElevation':
        pos = loc['c']
    else:
        lg.warning(f'Unused location format: {loc_format}')
        return None

    return {
        'loc': {'polar': {'bear': pos['bearing'], 'elev': pos['elevation']}}
    }


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    target = params.get('target')
    if target == 'flightlog':

        def build_position(loc, geoid):
            return _build_cartesian_position(loc, geoid)

    elif target == 'radarlog':

        def build_position(loc, geoid):
            return _build_polar_position(loc)

    else:
        raise ValueError(f'Unsupported content type: {params.get("content")}')

    geoid = u.load_geoid(params, metadata)
    metadata.update({'content': target, 'source': 'courageous'})
    output.write(metadata)

    data = json.loads(input_path.read_text())
    entries = []

    for track in data.get('tracks', []):
        track_name = track.get('name', 'unknown')
        track_id = track.get('uas_id', 'noid')

        uaid = {
            'int': f'{track_name}-{track_id}',
        }

        for record in track.get('records', []):
            flog_record = {'time': {'unix': record['time']}, 'uaid': uaid}
            position = build_position(record['location'], geoid)

            if position:
                flog_record['pos'] = position

            entries.append(flog_record)

    entries.sort(key=lambda e: e['time']['unix'])

    for entry in entries:
        output.write(entry)
