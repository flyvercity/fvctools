from pathlib import Path
import logging as lg
from zipfile import ZipFile
import math

import simplekml

import fvc.tools.df.util as u


def generate_point(params, record, kml):
    loc = record['pos']['loc']

    pnt = kml.newpoint(
        coords=[(loc['lon'], loc['lat'], loc['alt'])],
        extrude=1,
        altitudemode = simplekml.AltitudeMode.absolute
    )

    pnt.style.iconstyle.scale = 1

    if yaw := record.get('pos', {}).get('att', {}).get('yaw'):
        pnt.style.iconstyle.heading = yaw
        pnt.style.iconstyle.icon.href = 'images/arrow.png'
    else:
        pnt.style.iconstyle.icon.href = 'images/circle.png'
    

def generate_line(params, record, curr_pos, kml):
    pos = record['pos']
    loc = pos['loc']

    kml.newlinestring(
        coords=[
            (curr_pos['lon'], curr_pos['lat'], curr_pos['alt']),
            (loc['lon'], loc['lat'], loc['alt'])
        ],
        altitudemode = simplekml.AltitudeMode.absolute
    )

    
    curr_pos['lat'] = loc['lat']
    curr_pos['lon'] = loc['lon']
    curr_pos['alt'] = loc['alt']


def generate_features(params, record, curr_pos, kml):
    generate_point(params, record, kml)
    generate_line(params, record, curr_pos, kml)


def export_from_fvc(params, output_path: Path | None):
    input_path = params['input'].fetch()

    if not output_path:
        output = input_path.with_suffix('.kmz')  # type: Path
    else:
        output = output_path

    kml = simplekml.Kml()

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

        for record in io.iterate():
            try:
                generate_features(params, record, curr_pos, kml)
            except UserWarning as e:
                lg.warning(f'Unable to process record: {e}')
                continue

        kml_string = kml.kml()
        arrow = Path(__file__).parent / 'images' / 'arrow.png'
        arrow = Path(__file__).parent / 'images' / 'circle.png'
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with ZipFile(output, 'w') as kmz:
            kmz.writestr('doc.kml', kml_string)
            kmz.write(arrow, 'images/arrow.png')
            kmz.write(arrow, 'images/circle.png')

        return output
