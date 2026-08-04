from pathlib import Path

import click

import fvc.tools.df.xformats.nmea as nmea
from fvc.tools.utils import JSON


def metadata_args(command_func):
    command_func = click.option(
        '--polar-sensor-format',
        help='Format for polar sensor information',
        type=click.Choice(['nmea']),
    )(command_func)
    command_func = click.option(
        '--polar-sensor-source',
        help='Add polar sensor information to metadata for this file',
        type=click.Path(exists=True, path_type=Path),
    )(command_func)
    command_func = click.option(
        '--attach-polar-sensor',
        help='Attach polar sensor information to metadata for this file',
        is_flag=True,
    )(command_func)
    return command_func


def create_metadata(origin, params) -> JSON:
    metadata = {
        'origin': origin,
    }

    if params.get('attach_polar_sensor'):
        metadata.update(attach_polar_sensor(params))

    return metadata


def attach_polar_sensor(params) -> JSON:
    if not params.get('attach_polar_sensor'):
        raise UserWarning('Polar sensor information not attached')

    if not params.get('polar_sensor_source'):
        raise UserWarning('Polar sensor source not provided')

    polar_sensor_source = params['polar_sensor_source']
    polar_sensor_format = params['polar_sensor_format']
    metadata = {}

    if polar_sensor_format == 'nmea':
        metadata['polar_sensor'] = {
            'source': 'nmea',
            'origin': polar_sensor_source.name,
            'loc': nmea.extract_sensor_data(params, polar_sensor_source),
        }

        return metadata

    raise UserWarning(f'Unknown sensor format: {polar_sensor_format}')
