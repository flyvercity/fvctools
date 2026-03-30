import json
from typing import Any, Dict
from datetime import UTC, datetime

import polars as pl
from dateutil import parser as dateparser
from pygeodesy import dms
from rich import print_json

JSON = Dict[str, Any]
JSON_INDENT = 2


def json_print(params, data: JSON):
    if not params['no_pprint']:
        print_json(data=json.dumps(data, indent=JSON_INDENT, sort_keys=True))
    else:
        print(json.dumps(data))


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
            return sign * (deg + min / 60.0)

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
            return sign * (deg + min / 60.0)

    # Something else
    return dms.parseDMS(lon)


def render_latlon(lat, lon) -> str:
    return f'{dms.latDMS(lat, dms.F_DMS)} {dms.lonDMS(lon, dms.F_DMS)}'


def plnested(selector: str):
    col, *fields = selector.split('.')
    e = pl.col(col)

    for f in fields:
        e = e.struct.field(f)

    return e


def datestring_to_ts(datestr: str) -> int:
    try:
        # ⚡ Bolt: Fast path for ISO-8601 strings (e.g. from JSON or log files).
        # datetime.fromisoformat is ~40x faster than dateutil.parser.parse
        dt = datetime.fromisoformat(datestr.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return int(dt.timestamp() * 1000)
    except ValueError:
        pass

    dt = dateparser.parse(datestr)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return int(dt.timestamp() * 1000)
