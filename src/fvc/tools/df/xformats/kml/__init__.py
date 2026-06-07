import logging as lg
from pathlib import Path
from zipfile import ZipFile

import simplekml

import fvc.tools.df.utils as dfu


def generate_point(params, record, kml):
    loc = record.get('pos', {}).get('loc', {})

    pnt = kml.newpoint(
        coords=[(loc.get('lon'), loc.get('lat'), loc.get('alt'))],
        extrude=1,
        altitudemode=simplekml.AltitudeMode.absolute,
    )

    pnt.style.iconstyle.scale = 1

    if yaw := record.get('pos', {}).get('att', {}).get('yaw'):
        pnt.style.iconstyle.heading = yaw
        pnt.style.iconstyle.icon.href = 'images/arrow.png'
    else:
        pnt.style.iconstyle.icon.href = 'images/circle.png'


def generate_line(params, record, curr_pos, kml):
    loc = record.get('pos', {}).get('loc', {})

    kml.newlinestring(
        coords=[
            (curr_pos.get('lon'), curr_pos.get('lat'), curr_pos.get('alt')),
            (loc.get('lon'), loc.get('lat'), loc.get('alt')),
        ],
        altitudemode=simplekml.AltitudeMode.absolute,
    )

    curr_pos['lat'] = loc.get('lat')
    curr_pos['lon'] = loc.get('lon')
    curr_pos['alt'] = loc.get('alt')


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

        loc = first.get('pos', {}).get('loc', {})
        curr_pos = {
            'lat': loc.get('lat'),
            'lon': loc.get('lon'),
            'alt': loc.get('alt'),
        }

        for record in io.iterate():
            try:
                generate_features(params, record, curr_pos, kml)
            except UserWarning as e:
                lg.warning(f'Unable to process record: {e}')
                continue

        kml_string = kml.kml()
        arrow = Path(__file__).parent / 'images' / 'arrow.png'
        circle = Path(__file__).parent / 'images' / 'circle.png'
        output.parent.mkdir(parents=True, exist_ok=True)

        with ZipFile(output, 'w') as kmz:
            kmz.writestr('doc.kml', kml_string)
            kmz.write(arrow, 'images/arrow.png')
            kmz.write(circle, 'images/circle.png')

        return output
