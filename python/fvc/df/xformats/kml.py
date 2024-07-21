from pathlib import Path
import logging as lg

import simplekml


import fvc.df.util as u


def generate_point(params, record, kml):
    pos = record['pos']
    loc = pos['loc']

    pnt = kml.newpoint(
        coords=[(loc['lon'], loc['lat'], loc['alt'])],
        extrude=1
    )

    pnt.style.iconstyle.scale = 1
    pnt.style.iconstyle.icon.href = 'https://maps.google.com/mapfiles/kml/pal4/icon16.png'
    pnt.altitudemode = simplekml.AltitudeMode.absolute
    

def generate_line(params, record, curr_pos, kml):
    pos = record['pos']
    loc = pos['loc']

    line = kml.newlinestring(coords=[
        (curr_pos['lon'], curr_pos['lat'], curr_pos['alt']),
        (loc['lon'], loc['lat'], loc['alt'])
    ])

    line.altitudemode = simplekml.AltitudeMode.absolute
    
    curr_pos['lat'] = loc['lat']
    curr_pos['lon'] = loc['lon']
    curr_pos['alt'] = loc['alt']


def generate_features(params, record, curr_pos, kml):
    generate_point(params, record, kml)
    generate_line(params, record, curr_pos, kml)


def export_from_fvc(params, output_path: Path | None):
    input_path = params['input_file'].fetch()

    if not output_path:
        output = input_path.with_suffix('.kml')  # type: Path
    else:
        output = output_path

    kml = simplekml.Kml()

    with u.JsonlinesIO(input_path, 'rt') as io:
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
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(kml_string)
        return output
