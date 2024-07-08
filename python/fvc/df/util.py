import json
from pathlib import Path
from typing import Any, Dict
import logging as lg
import os

import boto3

type JSON = Dict[str, Any]


class JsonlinesIO:
    def __init__(self, filepath: Path, mode: str):
        self._filepath = filepath
        self._mode = mode
        self._file = None

    def __enter__(self):
        self._file = self._filepath.open(self._mode, encoding='utf-8', newline=None)
        self._in_line_no = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()

    def _check_entered(self):
        if not self._file:
            raise UserWarning('Enter context before using the object')

    def read(self) -> JSON | None:
        self._check_entered()
        line = self._file.readline()
        self._in_line_no += 1

        if not line.strip():
            return None

        return json.loads(line)

    def write(self, data):
        self._check_entered()
        self._file.write(json.dumps(data) + '\n')

    def iterate(self):
        while data := self.read():
            yield data


def progress_bar(bytes_amount):
    lg.info(f'Downloaded {bytes_amount} bytes')


def fetch_input_file(args=None, input_filename=None) -> Path:
    if not input_filename:
        if not args:
            raise UserWarning('CLI arguments not specified')

        input_filename = args.input_file

    if not input_filename:
        raise UserWarning('Input file not specified')

    path = Path(input_filename)

    if input_filename.startswith('s3://'):
        cache_dir = os.getenv('FVC_CACHE')

        if args and args.cache_dir:
            cache_dir = args.cache_dir

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

    raise UserWarning(f'Unable to resolve input file: {input_filename}')
