import click
from functools import wraps
import logging as lg

from fvc.df.util import fetch_input_file, JSON
import fvc.df.nmea as nmea


def metadata_args(command_func):
    @click.option(
        '--polar-sensor-source',
        help='Add polar sensor information to metadata for this file',
        type=str
    )
    @click.option(
        '--polar-sensor-format',
        help='Format for polar sensor information',
        type=click.Choice(['nmea'])
    )
    @wraps(command_func)
    def wrapper(*args, **kwargs):
        command_func(*args, **kwargs)

    return wrapper


def add_metadata_params(params, polar_sensor_source, polar_sensor_format):
    if not polar_sensor_source:
        return

    lg.debug(f'Adding polar params: {polar_sensor_source}, {polar_sensor_format}')

    params['polar'] = {
        'sensor_source': polar_sensor_source,
        'sensor_format': polar_sensor_format
    }

    return params


def initial_metadata(params) -> JSON:
    metadata = {}  # type: JSON
    metadata['origin'] = str(params['input_file'].name)

    if 'polar' not in params:
        return metadata

    filename = params['polar']['sensor_source']
    source = fetch_input_file(params, filename)

    if format := params['polar'].get('sensor_format'):
        if format == 'nmea':
            metadata['polar_sensor'] = {
                'source': 'nmea',
                'origin': source.name
            }

            metadata['polar_sensor'].update(
                nmea.extract_sensor_data(params, source)
            )

            return metadata

    raise UserWarning(f'Unknown sensor format: {format}')
