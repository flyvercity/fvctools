import json
from pathlib import Path

from fvc.tools.df.utils import JsonlinesIO, lg
from fvc.tools.calc.geoid import load_geoid, amsl_to_ellipsoidal


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    target = params.get('target')
    if target not in ('flightlog', 'radarlog'):
        raise ValueError(f'Unsupported target type: {target}')

    geoid = load_geoid(params, metadata)
    metadata.update({'content': target, 'source': 'courageous'})
    output.write(metadata)

    data = json.loads(input_path.read_text())
    entries = []

    for track in data.get('tracks', []):
        track_name = track.get('name', 'unknown')
        track_id = track.get('uas_id', 'noid')
        uaid = {'int': f'{track_name}-{track_id}'}

        for record in track.get('records', []):
            loc = record.get('location', {})
            position = None

            if target == 'flightlog':
                if 't' in loc and loc['t'] == 'Position3d':
                    pos = loc['c']
                elif 'Position3d' in loc:
                    pos = loc['Position3d']
                else:
                    lg.warning(f'Unused location format: {loc.get("t")}')
                    continue

                lat = pos['lat']
                lon = pos['lon']
                amsl = pos['height_amsl']
                alt = amsl_to_ellipsoidal(geoid, lat, lon, amsl)
                position = {'loc': {'lat': lat, 'lon': lon, 'alt': alt}}

            elif target == 'radarlog':
                loc_format = loc.get('t')
                if loc_format == 'BearingElevation':
                    pos = loc['c']
                else:
                    lg.warning(f'Unused location format: {loc_format}')
                    continue

                position = {'loc': {'polar': {'bear': pos['bearing'], 'elev': pos['elevation']}}}

            if position:
                entries.append(
                    {
                        'time': {'unix': record['time']},
                        'uaid': uaid,
                        'pos': position,
                    }
                )

    entries.sort(key=lambda e: e['time']['unix'])
    for entry in entries:
        output.write(entry)
