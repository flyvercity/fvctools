import json
from pathlib import Path
from typing import Any, Dict
import logging as lg

import boto3

type JSON = Dict[str, Any]


class JsonlinesIO:
    def __init__(self, filepath: Path, mode: str):
        self._filepath = filepath
        self._mode = mode

    def __enter__(self):
        self._file = self._filepath.open(self._mode, encoding='utf-8', newline=None)
        self._in_line_no = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()

    def read(self) -> JSON | None:
        line = self._file.readline()
        self._in_line_no += 1

        if not line.strip():
            return None

        return json.loads(line)

    def write(self, data):
        self._file.write(json.dumps(data) + '\n')


def progress_bar(bytes_amount):
    lg.info(f'Downloaded {bytes_amount} bytes')


def fetch_input_file(args, input_filename=None) -> Path:
    if not input_filename:
        input_filename = args.input_file

    if not input_filename:
        raise UserWarning('Input file not specified')

    path = Path(input_filename)

    if input_filename.startswith('s3://'):
        if not args.cache_dir:
            raise UserWarning('Cache directory should be specified for external data')

        cache_dir = Path(args.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        rel_path = path.relative_to('s3://')
        local_path = (Path(args.cache_dir) / rel_path).resolve()

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
