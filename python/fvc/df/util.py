import json
from pathlib import Path
from typing import Any, Dict


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

    def read(self) -> Dict[str, Any] | None:
        line = self._file.readline()
        self._in_line_no += 1

        if not line.strip():
            return None

        return json.loads(line)

    def write(self, data):
        self._file.write(json.dumps(data) + '\n')
