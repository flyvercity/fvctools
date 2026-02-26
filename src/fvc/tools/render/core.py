import logging as lg
from datetime import UTC, datetime
from itertools import islice
from pathlib import Path
from typing import Any, Dict, List

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.render.templates import (
    generate_html_template,
    generate_js_template,
)


def generate_html_map(file_path: Path, output_dir: Path, title: str):
    """Generate an interactive map visualization for FVC data files.

    Args:
        file_path: Path to the FVC data file (jsonlines format)
        output_dir: Directory to save the visualization files
        title: Title for the visualization
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    lg.info('Extracting coordinate data from file...')
    coordinates = extract_coordinates(file_path)

    if not coordinates:
        raise ValueError('No valid coordinate data found in the file')

    lg.info(f'Extracted {len(coordinates)} coordinate points')

    bounds = calculate_bounds(coordinates)
    lg.info(f'Map bounds: {bounds}')

    html_content = generate_html_template(
        title=title,
        generation_time=datetime.now(tz=UTC).strftime('%Y-%m-%d %H:%M:%S'),
        file_path=file_path.name,
        coordinates=coordinates,
        bounds=bounds,
    )

    lg.info('Generating HTML file...')
    html_path = output_dir / 'index.html'
    html_path.write_text(html_content)

    lg.info('Generating JavaScript file...')
    js_content = generate_js_template()
    js_path = output_dir / 'map.js'
    js_path.write_text(js_content)

    lg.info(f'Generated visualization files: {html_path}, {js_path}')


def extract_coordinates(file_path: Path) -> List[Dict[str, Any]]:
    """Extract latitude and longitude coordinates from FVC data file.

    Args:
        file_path: Path to the FVC data file

    Returns:
        List of coordinate dictionaries with lat, lon, and metadata
    """

    coordinates = []

    with JsonlinesIO(file_path, mode='r') as reader:
        for record in reader.iterate():
            # Check if this is a flightlog record with position data
            if record.get('pos') and record.get('pos.loc'):
                lat = record.get('pos.loc.lat')
                lon = record.get('pos.loc.lon')

                if lat is not None and lon is not None:
                    try:
                        coord_data = {
                            'lat': float(str(lat)),
                            'lon': float(str(lon)),
                            'time': record.get('time.unix'),
                            'altitude': record.get('pos.loc.alt'),
                            'amsl': record.get('pos.loc.amsl'),
                            'height': record.get('pos.loc.height'),
                        }

                        # Add cellular signal data if available
                        if record.get('cellsig'):
                            coord_data.update(
                                {
                                    'rsrp': record.get('cellsig.RSRP'),
                                    'rsrq': record.get('cellsig.RSRQ'),
                                    'plmnid': record.get('cellsig.plmnid'),
                                    'plmnname': record.get('cellsig.plmnname'),
                                }
                            )

                        coordinates.append(coord_data)

                    except (ValueError, TypeError) as e:
                        lg.warning(f'Skipping invalid coordinate data: {e}')
                        continue

    return coordinates


def calculate_bounds(coordinates: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate the bounding box for the map.

    Args:
        coordinates: List of coordinate dictionaries

    Returns:
        Dictionary with north, south, east, west bounds
    """

    if not coordinates:
        return {'north': 0, 'south': 0, 'east': 0, 'west': 0}

    first = coordinates[0]
    north = south = first['lat']
    east = west = first['lon']

    for coord in islice(coordinates, 1, None):
        lat = coord['lat']
        lon = coord['lon']

        if lat > north:
            north = lat
        elif lat < south:
            south = lat

        if lon > east:
            east = lon
        elif lon < west:
            west = lon

    return {
        'north': north,
        'south': south,
        'east': east,
        'west': west,
    }
