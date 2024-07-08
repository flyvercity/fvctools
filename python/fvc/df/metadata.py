from fvc.df.util import fetch_input_file, JSON
import fvc.df.nmea as nmea


def add_metadata_args(parser):
    parser.add_argument(
        '--polar-sensor-source',
        help='Add polar sensor information to metadata for this file',
        type=str
    )

    parser.add_argument(
        '--polar-sensor-format',
        help='Format for polar sensor information',
        choices=['nmea']
    )


def initial_metadata(args) -> JSON:
    metadata = {}  # type: JSON

    sensor_filename = args.polar_sensor_source

    if not sensor_filename:
        return metadata

    sensor_source = fetch_input_file(args, sensor_filename)

    if sensor_format := args.polar_sensor_format:
        if sensor_format == 'nmea':
            metadata['polar_sensor'] = {
                'source': 'nmea',
                'origin': sensor_source.name
            }

            metadata['polar_sensor'].update(
                nmea.extract_sensor_data(args, sensor_source)
            )

            return metadata

    raise UserWarning(f'Unknown sensor format: {sensor_format}')
