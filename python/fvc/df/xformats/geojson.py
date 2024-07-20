from pathlib import Path
import json
import logging as lg


import fvc.df.util as u


def generate_feature(params, record):
    pos = record['pos']
    loc = pos['loc']

    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [
                loc['lon'],
                loc['lat'],
                loc['alt']
            ]
        },
        'properties': {}
    }

    if params['with_cellular']:
        if 'cellsig' not in record:
            raise UserWarning('Cellular signal data not found')
        
        signal = record['cellsig']
        feature['properties'] = {'rsrp': signal['RSRP']}

    return feature


def generate_geojson(features):
    collection = {
        'type': 'FeatureCollection',
        'features': features
    }

    return json.dumps(collection, indent=2)


def export_from_fvc(params, output_path: Path | None):
    input_path = params['input_file'].fetch()

    if not output_path:
        output = input_path.with_suffix('.geo.json')  # type: Path
    else:
        output = output_path

    with u.JsonlinesIO(input_path, 'rt') as io:
        metadata = io.read()

        if not metadata:
            raise UserWarning('No metadata found')

        if (content := metadata.get('content')) != 'flightlog':
            raise UserWarning(f'Unsupported content type: {content}')

        features = []

        for record in io.iterate():
            try:
                features.append(generate_feature(params, record))
            except UserWarning as e:
                lg.warning(f'Unable to process record: {e}')
                continue

        geojson = generate_geojson(features)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(geojson)
        return output
