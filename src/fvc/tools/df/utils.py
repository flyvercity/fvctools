import json
import logging
from pathlib import Path
from typing import Generator, Literal

from benedict import benedict
import polars as pl


lg = logging.getLogger('fvc.tools.df')


class JsonlinesIO:
    def __init__(
        self,
        filepath: Path,
        mode: Literal['r', 'w'],
        callback=None,
        raw: bool = False,
    ):
        self._filepath = filepath
        self._mode = mode
        self._file = None  # IO | None
        self._callback = callback
        self._pos = 0
        # Performance optimization: if True, skip benedict wrapping for read operations
        self._raw = raw

    def stat_size(self):
        # NOTE: This is used by external code, do not delete
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

    def read(self) -> benedict | dict | None:
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

        data = json.loads(line)

        if self._raw:
            # Skip benedict wrapping for performance
            return data

        return benedict(data)

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

    def iterate(self) -> Generator[benedict | dict, None, None]:
        while data := self.read():
            yield data


def input_path(params: benedict) -> Path:
    param = params.get('input_path')

    if not param:
        raise UserWarning('Input path is not set, use --in to set it')

    path = Path(param)

    if suffix := params.get('suffix'):
        path = path.with_suffix(suffix)

    return path


class FvcDataset:
    @staticmethod
    def read(filepath: Path) -> 'FvcDataset':
        with JsonlinesIO(filepath, 'r') as io:
            metadata = io.read()
            df = pl.read_ndjson(io._file)
            return FvcDataset(metadata, df)

    def __init__(self, metadata: benedict, df: pl.DataFrame):
        self._metadata = metadata
        self._df = df

    @property
    def metadata(self) -> benedict:
        return self._metadata

    @property
    def df(self) -> pl.DataFrame:
        return self._df
