from functools import wraps
from pathlib import Path

import click

import fvc.tools.df.xformats.nmea as nmea
from fvc.tools.utils import JSON


def metadata_args(command_func):
    @click.option(
        '--polar-sensor-source',
        help='Add polar sensor information to metadata for this file',
        type=str,
    )
    @click.option(
        '--polar-sensor-format',
        help='Format for polar sensor information',
        type=click.Choice(['nmea']),
    )
    @wraps(command_func)
    def wrapper(*args, **kwargs):
        command_func(*args, **kwargs)

    return wrapper


# TODO: move this to "custom" parameters
def initial_metadata(origin, params) -> JSON:
    metadata = {}  # type: JSON
    metadata['origin'] = origin

    polar_sensor_source = params.get('polar_sensor_source') or params.get(
        'polar-sensor-source'
    )
    polar_sensor_format = params.get('polar_sensor_format') or params.get(
        'polar-sensor-format'
    )

    if not polar_sensor_source:
        return metadata

    if not polar_sensor_format:
        raise UserWarning(
            'Sensor format (--polar-sensor-format) must be provided'
        )

    source = Path(polar_sensor_source)

    if polar_sensor_format == 'nmea':
        metadata['polar_sensor'] = {'source': 'nmea', 'origin': source.name}

        metadata['polar_sensor'].update(
            nmea.extract_sensor_data(params, source)
        )

        return metadata

    raise UserWarning(f'Unknown sensor format: {format}')
