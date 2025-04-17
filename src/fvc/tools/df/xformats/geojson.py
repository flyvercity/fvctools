from pathlib import Path
import json
import logging as lg


import fvc.tools.df.util as u


def generate_point(params, record):
    pos = record['pos']
    loc = pos['loc']

    point = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [loc['lon'], loc['lat'], loc['alt']]
        },
        'properties': {}
    }

    if params['with_cellular']:
        if 'cellsig' not in record:
            raise UserWarning('Cellular signal data not found')

        signal = record['cellsig']
        point['properties'] = {'rsrp': signal['RSRP']}

    return point


def generate_line(params, record, curr_pos):
    pos = record['pos']
    loc = pos['loc']

    line = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [
                [curr_pos['lon'], curr_pos['lat'], curr_pos['alt']],
                [loc['lon'], loc['lat'], loc['alt']]
            ]
        },
        'properties': {}
    }

    curr_pos['lat'] = loc['lat']
    curr_pos['lon'] = loc['lon']
    curr_pos['alt'] = loc['alt']

    return line


def generate_features(params, record, curr_pos):
    return [
        generate_point(params, record),
        generate_line(params, record, curr_pos)

    ]


def generate_geojson(features):
    collection = {
        'type': 'FeatureCollection',
        'features': features
    }

    return json.dumps(collection, indent=2)


def export_from_fvc(params, output_path: Path | None):
    input_path = params['input'].fetch()

    if not output_path:
        output = input_path.with_suffix('.geo.json')  # type: Path
    else:
        output = output_path

    with u.JsonlinesIO(input_path, 'r') as io:
        metadata = io.read()

        if not metadata:
            raise UserWarning('No metadata found')

        if (content := metadata.get('content')) != 'flightlog':
            raise UserWarning(f'Unsupported content type: {content}')

        first = io.read()

        if not first:
            return

        curr_pos = {
            'lat': first['pos']['loc']['lat'],
            'lon': first['pos']['loc']['lon'],
            'alt': first['pos']['loc']['alt']
        }

        features = []

        for record in io.iterate():
            try:
                features.extend(generate_features(params, record, curr_pos))
            except UserWarning as e:
                lg.warning(f'Unable to process record: {e}')
                continue

        geojson = generate_geojson(features)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(geojson)
        return output
