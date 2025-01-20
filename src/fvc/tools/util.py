import json
from datetime import UTC
import logging as lg
from pathlib import Path

from typing import Any, Dict
from pygments import highlight
from pygments.lexers.jsonnet import JsonnetLexer
from pygments.formatters import TerminalFormatter
from pygeodesy import dms
from dateutil import parser as dateparser
from pygeodesy.geoids import GeoidPGM


JSON = Dict[str, Any]
JSON_INDENT = 2


def json_print(params, data: JSON):        
    if not params['no_pprint']:
        json_str = json.dumps(data, indent=JSON_INDENT, sort_keys=True)
        print(highlight(json_str, JsonnetLexer(), TerminalFormatter()))
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


def parse_lat(lat: Any) -> float:
    # Try to detect the NMEA-0183 format
    if isinstance(lat, str):
        split = lat.split('.')

        if len(split) == 2 and len(split[0]) == 4:
            lat = lat.replace(',', '')

            if lat[-1] in ['N', 'S']:
                sign = -1 if lat[-1] == 'S' else 1
                lat = lat[:-1]
            else:
                sign = 1

            deg = int(lat[:2])
            min = float(lat[2:])
            return sign*(deg + min/60.0)
        
    # Something else
    return dms.parseDMS(lat)


def parse_lon(lon: Any) -> float:
    # Try to detect the NMEA-0183 format
    if isinstance(lon, str):
        split = lon.split('.')

        if len(split) == 2 and len(split[0]) == 5:
            lon = lon.replace(',', '')

            if lon[-1] in ['W', 'E']:
                sign = -1 if lon[-1] == 'W' else 1
                lon = lon[:-1]
            else:
                sign = 1

            deg = int(lon[:3])
            min = float(lon[3:])
            return sign*(deg + min/60.0)
        
    # Something else
    return dms.parseDMS(lon)


def render_latlon(lat, lon) -> str:
    return f'{dms.latDMS(lat, dms.F_DMS)} {dms.lonDMS(lon, dms.F_DMS)}'
