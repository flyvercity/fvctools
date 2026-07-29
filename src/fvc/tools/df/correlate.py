from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from fvc.tools.df.utils import JsonlinesIO, lg


def correlate(
    params: dict[str, Any],
    infiles: tuple[Path, ...],
    check_callbacks: list[Callable[[int], None]],
):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(_ensure_sorting, infile, check_callbacks[i]) for i, infile in enumerate(infiles)]

        results = []
        errors = []

        for future in futures:
            result, error = future.result()
            results.append(result)

            if error:
                errors.append(error)

        if not all(results):
            raise UserWarning(errors)


def _ensure_sorting(infile: Path, check_callback: Callable[[int], None]):
    lg.debug(f'Checking {infile}...')

    time = None

    # ⚡ Bolt: Enable raw=True to skip benedict wrapping for performance.
    # Sorting check only needs 'time.unix', so we avoid the ~25x overhead of benedict.
    with JsonlinesIO(infile, 'r', callback=check_callback, raw=True) as reader:
        for record in reader.iterate():
            # Skip metadata record (first line) which doesn't have a 'time' field.
            if 'time' not in record:
                continue

            # Use standard dict access instead of benedict dot-notation.
            record_time = record['time']['unix']

            if time is None:
                time = record_time
            else:
                if record_time < time:
                    return False, f'{infile} is not sorted by time'

            time = record_time

    return True, None
