import logging as lg
from pathlib import Path
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor

from fvc.tools.df.utils import JsonlinesIO


def correlate(
    params: dict[str, Any],
    infiles: tuple[Path, ...],
    check_callbacks: list[Callable[[int], None]],
    merge_callback: Callable[[int], None]
):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_ensure_sorting, infile, check_callbacks[i])
            for i, infile in enumerate(infiles)
        ]

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

    with JsonlinesIO(infile, 'r', callback=check_callback) as reader:
        for record in reader.iterate():
            record_time = record.get_int('time.unix')

            if time is None:
                time = record_time
            else:
                if record_time < time:
                    return False, f'{infile} is not sorted by time'

            time = record_time

    return True, None
