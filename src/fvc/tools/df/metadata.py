import click
from functools import wraps
import logging as lg

from fvc.tools.util import JSON
from fvc.tools.df.util import Input
import fvc.tools.df.xformats.nmea as nmea


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


def initial_metadata(params) -> JSON:
    metadata = {}  # type: JSON
    metadata['origin'] = str(params['input'].fetch().name)

    if not params.get('polar_sensor_source'):
        return metadata

    if not 'polar_sensor_format' in params:
        raise UserWarning('Sensor format (--polar-sensor-format) must be provided')

    filename = params['polar_sensor_source']
    source = Input(params, filename).fetch()

    if format := params.get('polar_sensor_format'):
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
