from pathlib import Path
from typing import TypedDict
from datetime import datetime

from benedict import benedict
import fvc.tools.df.utils as u


class SplitParams(TypedDict):
    input_path: Path
    output_dir: Path
    verbose: bool
    inactivity_threshold_seconds: float


def split_by_day(params: SplitParams, callback=None) -> list[Path]:
    input_path = u.input_path(params)
    output_dir = params['output_dir']
    output_dir.mkdir(parents=True, exist_ok=True)
    current_day = None
    current_output = None
    output_files = []

    with u.JsonlinesIO(input_path, 'r', callback=callback) as input:
        metadata = input.read()

        for record in input.iterate():
            time = record['time']['unix']
            day = datetime.fromtimestamp(time / 1000.0).date()

            if not current_output or day != current_day:
                current_day = day

                if current_output:
                    output_path = _save_output(
                        day,
                        output_dir,
                        metadata,
                        current_output,
                    )

                    output_files.append(output_path)

                current_output = []

            current_output.append(record)

    if current_output:
        _save_output(
            current_day,
            output_dir,
            metadata,
            current_output,
        )

    return output_files


def split_by_inactivity(params: SplitParams, callback=None) -> list[Path]:
    input_path = u.input_path(params)
    output_dir = params['output_dir']
    output_dir.mkdir(parents=True, exist_ok=True)
    threshold_seconds = params['inactivity_threshold_seconds']
    current_output = None
    previous_time = None
    file_counter = 0
    output_files = []

    with u.JsonlinesIO(input_path, 'r', callback=callback) as input:
        metadata = input.read()

        for record in input.iterate():
            time = record['time']['unix']
            time_seconds = time / 1000.0

            if previous_time is not None:
                gap_seconds = time_seconds - previous_time

                if gap_seconds > threshold_seconds:
                    if current_output:
                        output_path = _save_output_by_inactivity(
                            file_counter,
                            output_dir,
                            metadata,
                            current_output,
                        )

                        output_files.append(output_path)
                        file_counter += 1

                    current_output = []

            if current_output is None:
                current_output = []

            current_output.append(record)
            previous_time = time_seconds

    if current_output:
        output_path = _save_output_by_inactivity(
            file_counter,
            output_dir,
            metadata,
            current_output,
        )
        output_files.append(output_path)

    return output_files


def _save_output(
    current_day: datetime,
    output_dir: Path,
    metadata: benedict,
    records: list[benedict],
):
    output_path = output_dir / f'{current_day.strftime('%Y%m%d')}.fvc'

    with u.JsonlinesIO(output_path, 'w') as output:
        output.write(metadata)

        for record in records:
            output.write(record)

    return output_path


def _save_output_by_inactivity(
    file_counter: int,
    output_dir: Path,
    metadata: benedict,
    records: list[benedict],
):
    if not records:
        return

    start_time = datetime.fromtimestamp(records[0]['time']['unix'] / 1000.0)
    end_time = datetime.fromtimestamp(records[-1]['time']['unix'] / 1000.0)
    time_str = f'{start_time.strftime("%Y%m%d_%H%M%S")}-{end_time.strftime("%H%M%S")}'
    output_path = output_dir / f'{file_counter:03d}_{time_str}.fvc'

    with u.JsonlinesIO(output_path, 'w') as output:
        output.write(metadata)

        for record in records:
            output.write(record)

    return output_path
