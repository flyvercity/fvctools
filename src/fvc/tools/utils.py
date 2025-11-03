import json
import logging as lg
from pathlib import Path
from typing import Any, Dict
from datetime import UTC

from dateutil import parser as dateparser
from pygeodesy import dms
from pygeodesy.geoids import GeoidPGM
from rich import print_json

JSON = Dict[str, Any]
JSON_INDENT = 2


def json_print(params, data: JSON):
    if not params['no_pprint']:
        print_json(data=json.dumps(data, indent=JSON_INDENT, sort_keys=True))
    else:
        print(json.dumps(data))


def load_geoid(params, metadata=None) -> GeoidPGM:
    pgm_path = Path(__file__).parent / 'static' / 'egm96-5.pgm'

    if egm := params.get('EGM'):
        pgm_path = Path(egm)

    lg.debug(f'Using geoid model: {pgm_path.absolute()}')

    if metadata:
        metadata.update({'geoid': pgm_path.name})

    geoid = GeoidPGM(pgm_path)
    return geoid


def amsl_to_ellipsoidal(geoid: GeoidPGM, lat: float, lon: float, amsl_height: float) -> float:
    # Initialize the Geoid model using EGM96 with WGS-84 datum
    geoid_height = geoid.height(lat, lon)
    ellipsoidal_height = amsl_height + geoid_height  # type: ignore
    return ellipsoidal_height


def datestring_to_ts(datestr: str) -> int:
    dt = dateparser.parse(datestr)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int(dt.timestamp() * 1000)


def _parse_nmea_coord(
    coord: Any,
    pre_dot_length: int,
    valid_suffixes: list[str],
    negative_suffix: str,
) -> float | None:
    # Try to detect the NMEA-0183 format
    if isinstance(coord, str):
        split = coord.split('.')

        if len(split) == 2 and len(split[0]) == pre_dot_length:
            coord = coord.replace(',', '')

            if coord[-1] in valid_suffixes:
                sign = -1 if coord[-1] == negative_suffix else 1
                coord = coord[:-1]
            else:
                sign = 1

            deg = int(coord[: pre_dot_length - 2])
            min = float(coord[pre_dot_length - 2 :])
            return sign * (deg + min / 60.0)

    return None


def parse_lat(lat: Any) -> float:
    result = _parse_nmea_coord(lat, 4, ['N', 'S'], 'S')
    if result is not None:
        return result

    # Something else
    return dms.parseDMS(lat)


def parse_lon(lon: Any) -> float:
    result = _parse_nmea_coord(lon, 5, ['W', 'E'], 'W')
    if result is not None:
        return result

    # Something else
    return dms.parseDMS(lon)


def render_latlon(lat, lon) -> str:
    return f'{dms.latDMS(lat, dms.F_DMS)} {dms.lonDMS(lon, dms.F_DMS)}'
