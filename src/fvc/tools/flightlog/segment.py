from pathlib import Path
from typing import TypedDict

import polars as pl

import fvc.tools.df.utils as dfu
from fvc.tools.flightlog.load import FlightlogDataset


class SegmentParams(TypedDict):
    input_path: Path
    verbose: bool = False
    segment_by_height: bool = False
    segment_height_meters: float
    airborne_only: bool
    segment_by_idle: bool
    segment_idle_time_seconds: float
    filter_by_duration: bool
    filter_duration_seconds: float


def segment(
    dataset: FlightlogDataset,
    params: SegmentParams,
    dump_steps: bool | None = None,
) -> tuple[FlightlogDataset, dict]:
    frames = dataset.frames
    metaproc = {}

    _dump(dump_steps, 'input', frames)

    if params['segment_by_height']:
        frames = segment_airborne(frames, params, metaproc)

        if params['airborne_only']:
            frames = [frame for frame in frames if frame['airborne'].max()]

    _dump(dump_steps, 'airborne', frames)

    if params['segment_by_idle']:
        frames = segment_by_idle(frames, params, metaproc)

    _dump(dump_steps, 'idle', frames)

    if params['filter_by_duration']:
        frames = filter_duration(frames, params, metaproc)

    _dump(dump_steps, 'duration', frames)

    result_dataset = dataset.evolve(
        frames=frames,
        metadata={
            'segment_by_height': params['segment_by_height'],
            'segment_by_idle': params['segment_by_idle'],
            'filter_by_duration': params['filter_by_duration'],
        },
    )

    metaproc.update(
        {
            'num_frames': len(result_dataset.frames),
        }
    )

    return result_dataset, metaproc


def segment_airborne(
    frames: list[pl.DataFrame],
    params: SegmentParams,
    metaproc: dict,
) -> list[pl.DataFrame]:
    segment = params['segment_height_meters']

    dfu.lg.info(f'Segmenting {len(frames)} frames by height {segment} meters')

    result_frames = []

    for frame in frames:
        frame = frame.with_columns(frame['derived_height'].gt(segment).alias('airborne'))

        change_idx = (frame['airborne'].shift(1) != frame['airborne']).fill_null(True).to_numpy().nonzero()[0]

        boundaries = list(change_idx) + [len(frame)]

        subframes = [frame.slice(start, stop - start) for start, stop in zip(boundaries, boundaries[1:])]

        dfu.lg.info(f'Segmented into {len(subframes)} frames by height {segment} meters')

        result_frames.extend(subframes)

    metaproc.update(
        {
            'segment_height_meters': segment,
            'segment_height_in': len(frames),
            'segment_height_out': len(result_frames),
        }
    )

    return result_frames


def segment_by_idle(
    frames: list[pl.DataFrame],
    params: SegmentParams,
    metaproc: dict,
) -> list[pl.DataFrame]:
    idle_time_milliseconds = params['idle_time_seconds'] * 1000.0

    dfu.lg.info(f'Segmenting by idle time {idle_time_milliseconds} milliseconds')

    result_frames = segment_by_timestamp(frames, idle_time_milliseconds)

    metaproc.update(
        {
            'segment_idle_time_ms': idle_time_milliseconds,
            'segment_idle_time_in': len(frames),
            'segment_idle_time_out': len(result_frames),
        }
    )

    return result_frames


def segment_by_timestamp(frames: list[pl.DataFrame], step_ms: int):
    result_frames = []

    for frame in frames:
        ts = frame['timestamp'].to_numpy()
        diffs = ts[1:] - ts[:-1]
        split_indices = (diffs > step_ms).nonzero()[0] + 1
        indices = [0] + split_indices.tolist() + [len(frame)]

        for start, end in zip(indices[:-1], indices[1:]):
            subframe = frame.slice(start, end - start)
            result_frames.append(subframe)

    return result_frames


def filter_duration(frames, params: SegmentParams, metaproc: dict):
    duration = params['filter_duration_seconds'] * 1000.0
    dfu.lg.info(f'Filtering by duration {duration} milliseconds')

    result_frames = [
        frame
        for frame in frames
        if frame['timestamp'].max() - frame['timestamp'].min() > duration
    ]

    dfu.lg.info(f'Filtered to {len(result_frames)} frames')

    metaproc.update(
        {
            'filter_duration_ms': duration,
            'filter_duration_in': len(frames),
            'filter_duration_out': len(result_frames),
        }
    )

    return result_frames


def _dump(dump_steps: bool, step: str, frames: list[pl.DataFrame]):
    if dump_steps:
        for inx, frame in enumerate(frames):
            frame.write_ndjson(Path(f'.tmp/dump_segment_{step}_{inx}'))
