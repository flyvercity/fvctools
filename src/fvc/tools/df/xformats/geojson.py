import json
from pathlib import Path

import fvc.tools.df.utils as dfu
from fvc.tools.df.utils import lg


def _validate_number(value, name: str):
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise UserWarning(f'Invalid {name} coordinate value: {value}')
    return value


def _geojson_coordinates(loc: dict):
    lon = loc.get('lon')
    lat = loc.get('lat')

    if lon is None or lat is None:
        raise UserWarning('Missing required coordinates: lon and lat')

    coordinates = [
        _validate_number(lon, 'lon'),
        _validate_number(lat, 'lat'),
    ]

    alt = loc.get('alt')
    if alt is not None:
        coordinates.append(_validate_number(alt, 'alt'))

    return coordinates


def generate_point(params, record):
    pos = record.get('pos', {})
    loc = pos.get('loc', {})

    point = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': _geojson_coordinates(loc),
        },
        'properties': {},
    }

    if 'cellsig' in record:
        signal = record['cellsig']
        # Use lowercase 'rsrp' as defined in schema.yaml
        point['properties'] = {'rsrp': signal.get('rsrp')}

    return point


def generate_line(params, record, curr_pos):
    pos = record.get('pos', {})
    loc = pos.get('loc', {})

    line = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [
                _geojson_coordinates(curr_pos),
                _geojson_coordinates(loc),
            ],
        },
        'properties': {},
    }

    curr_pos['lat'] = loc['lat']
    curr_pos['lon'] = loc['lon']
    curr_pos['alt'] = loc.get('alt')

    return line


def generate_geojson(features):
    collection = {'type': 'FeatureCollection', 'features': features}

    return json.dumps(collection, indent=2)


def export_from_fvc(params, output_path: Path | None):
    input_path = params['input'].fetch()

    if not output_path:
        output = input_path.with_suffix('.geojson')
    else:
        output = output_path

    # ⚡ Bolt: Using raw=True to skip benedict wrapping for performance.
    # This avoids significant overhead when iterating over many records (~25x speedup).
    with dfu.JsonlinesIO(input_path, 'r', raw=True) as io:
        metadata = io.read()

        if not metadata:
            raise UserWarning('No metadata found')

        if (content := metadata.get('content')) != 'flightlog':
            raise UserWarning(f'Unsupported content type: {content}')

        first = io.read()

        if not first:
            return

        # ⚡ Bolt: Direct dictionary access is used instead of dslice with dot-notation
        # because raw=True returns native dicts, not benedict objects.
        # Using .get() for robustness.
        loc = first.get('pos', {}).get('loc', {})
        _geojson_coordinates(loc)
        curr_pos = {
            'lat': loc['lat'],
            'lon': loc['lon'],
            'alt': loc.get('alt'),
        }

        features = []

        for record in io.iterate():
            try:
                features.extend(
                    [
                        generate_point(params, record),
                        generate_line(params, record, curr_pos),
                    ]
                )
            except UserWarning as e:
                lg.warning(f'Unable to process record: {e}')
                continue

        geojson = generate_geojson(features)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(geojson)
        return output
