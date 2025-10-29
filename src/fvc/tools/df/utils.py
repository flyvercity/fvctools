import json
import logging
from pathlib import Path
from typing import Generator, Literal

import boto3
from benedict import benedict
from rich.live import Live
from rich.spinner import Spinner


lg = logging.getLogger('fvc.tools.df')


class JsonlinesIO:
    def __init__(self, filepath: Path, mode: Literal['r', 'w'], callback=None):
        self._filepath = filepath
        self._mode = mode
        self._file = None  # IO | None
        self._callback = callback
        self._pos = 0

    def stat_size(self):
        return self._filepath.stat().st_size

    def __enter__(self):
        self._file = self._filepath.open(
            f'{self._mode}t', encoding='utf-8', newline=None
        )
        self._in_line_no = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            self._file.close()

    def _check_entered(self):
        if not self._file:
            raise UserWarning('Enter context before using the object')

    def read(self) -> benedict | None:
        self._check_entered()

        if self._file:
            line = self._file.readline()
        else:
            raise RuntimeError('File is not open')

        self._in_line_no += 1

        if self._callback:
            new_pos = self._file.tell()
            self._callback(new_pos - self._pos)
            self._pos = new_pos

        if not line.strip():
            return None

        return benedict(json.loads(line))

    def in_line_no(self):
        return self._in_line_no

    def write(self, data):
        self._check_entered()

        if self._file:
            line = json.dumps(data) + '\n'
            self._file.write(line)

            if self._callback:
                self._callback(len(line.encode('utf-8')))
        else:
            raise RuntimeError('File is not open')

    def iterate(self) -> Generator[benedict, None, None]:
        while data := self.read():
            yield data


class Input:
    def __init__(self, params, input_uri):
        self._params = params
        self._input_uri = input_uri

    def __str__(self) -> str:
        return str(self._input_uri)

    def as_dir(self):
        if not self._input_uri:
            raise UserWarning('Input file or URI (--in) is not specified')

        directory = Path(self._input_uri)

        if not directory.is_dir():
            raise UserWarning(f'Input is not a directory: {self}')

        return directory

    def fetch(self) -> Path:

        if not self._input_uri:
            raise UserWarning('Input file or URI (--in) is not specified')

        path = Path(self._input_uri)

        if suffix := self._params.get('suffix'):
            path = path.with_suffix(suffix)

        if str(self._input_uri).startswith('s3://'):
            cache_dir = self._params.get('cache_dir')

            if not cache_dir:
                raise UserWarning(
                    'Cache directory should be specified for external data'
                )

            cache_dir_path = Path(cache_dir)
            cache_dir_path.mkdir(parents=True, exist_ok=True)
            rel_path = path.relative_to('s3://flyvercity.datasets/')
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

            lg.info(f'Downloading to {local_path}')

            spinner = Spinner('aesthetic', 'Downloading...')

            with Live(spinner):
                s3.download_file(
                    bucket_name,
                    key,
                    str(local_path),
                    Callback=lambda x: spinner.update(
                        text=f'Downloaded {x} bytes'
                    ),
                )

            return local_path

        else:
            if path.exists():
                return path.resolve()

        raise UserWarning(f'Unable to resolve input file: {self}')
