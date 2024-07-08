from pathlib import Path
from typing import Dict, Any


def add_metadata_args(parser):
    parser.add_argument(
        '--polar-sensor-source',
        help='Add polar sensor information to metadata for this file',
        type=Path
    )

    parser.add_argument(
        '--polar-sensor-format',
        help='Format for polar sensor information',
        choices=['nmea']
    )


def initial_metadata(args) -> Dict[str, Any]:
    metadata = {}
    return metadata
