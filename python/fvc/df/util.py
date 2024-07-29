import json
from pathlib import Path
from typing import Literal, Any
import logging as lg
from datetime import UTC

import boto3
from pygeodesy.geoids import GeoidPGM
from pygeodesy import dms
from dateutil import parser as dateparser

from fvc.util import JSON

class JsonlinesIO:
    def __init__(self, filepath: Path, mode: Literal['r', 'w'], callback=None):
        self._filepath = filepath
        self._mode = mode
        self._file = None  # IO | None
        self._callback = callback

    def stat_size(self):
        return self._filepath.stat().st_size

    def __enter__(self):
        self._file = self._filepath.open(f'{self._mode}t', encoding='utf-8', newline=None)
        self._in_line_no = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            self._file.close()

    def _check_entered(self):
        if not self._file:
            raise UserWarning('Enter context before using the object')

    def read(self) -> JSON | None:
        self._check_entered()

        if self._file:
            line = self._file.readline()
        else:
            raise RuntimeError('File is not open')

        self._in_line_no += 1
        last_read_bytes = len(line) + 2  # \n\r

        if self._callback:
            self._callback(last_read_bytes)

        if not line.strip():
            return None

        return json.loads(line)

    def in_line_no(self):
        return self._in_line_no

    def write(self, data):
        self._check_entered()

        if self._file:
            self._file.write(json.dumps(data) + '\n')
        else:
            raise RuntimeError('File is not open')

    def iterate(self):
        while data := self.read():
            yield data


def progress_bar(bytes_amount):
    lg.info(f'Downloaded {bytes_amount} bytes')


class Input:
    def __init__(self, params, input_uri):
        self._params = params
        self._input_uri = input_uri

    def __str__(self) -> str:
        return str(self._input_uri)

    def as_dir(self):
        directory = Path(self._input_uri)

        if not directory.is_dir():
            raise UserWarning(f'Input is not a directory: {self}')
        
        return directory

    def fetch(self) -> Path:
        if not self._input_uri:
            raise UserWarning('Input file or URI (--input-file) is not specified')

        path = Path(self._input_uri)

        if self._input_uri.startswith('s3://'):
            cache_dir = self._params.get('cache_dir')

            if not cache_dir:
                raise UserWarning('Cache directory should be specified for external data')

            cache_dir_path = Path(cache_dir)
            cache_dir_path.mkdir(parents=True, exist_ok=True)
            rel_path = path.relative_to('s3://')
            local_path = (cache_dir_path / rel_path).resolve()

            if local_path.exists():
                lg.info(f'Using cached file: {local_path}')
                return local_path

            lg.info(f'Fetching to {local_path}')
            local_path.parent.mkdir(parents=True, exist_ok=True)
            bucket_name = path.parts[1]
            key = '/'.join(path.parts[2:])
            lg.debug(f'Bucket: {bucket_name}, Key: {key}')
            s3 = boto3.client('s3')
            s3.download_file(bucket_name, key, str(local_path), Callback=progress_bar)
            return local_path

        else:
            if path.exists():
                return path.resolve()

        raise UserWarning(f'Unable to resolve input file: {self}')


def load_geoid(params, metadata=None) -> GeoidPGM:
    pgm_path = Path(__file__).parent / 'egm96-5.pgm'

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


class JsonQuery:
    def __init__(self, query: str, default=None):
        path = query.split('.')

        def getter(data):
            for p in path:
                data = data.get(p) if data else None

            return data if data is not None else default
        
        self.getter = getter

    def __call__(self, data):
        return self.getter(data)


def parse_lat(lat: Any) -> float:
    # Try to detect NMEA format
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
    # Try to detect NMEA format
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
