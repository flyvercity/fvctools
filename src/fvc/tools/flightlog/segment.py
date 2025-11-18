from pathlib import Path
from typing import TypedDict

import polars as pl

import fvc.tools.df.utils as u
from fvc.tools.flightlog.load import FlightlogDataset


class SegmentParams(TypedDict):
    input_path: Path
    verbose: bool = False
    segment_by_height: bool = False
    segment_height_meters: float
    segment_by_idle: bool = False
    segment_idle_time_seconds: float
    filter_by_duration: bool = False
    filter_duration_seconds: float


def segment_airborne(
    frames: list[pl.DataFrame],
    params: SegmentParams,
    metaproc: dict,
) -> list[pl.DataFrame]:
    segment = params['segment_height_meters']

    u.lg.info(f'Segmenting {len(frames)} frames by height {segment} meters')

    result_frames = []

    for frame in frames:
        frame = frame.with_columns(
            frame['derived_height'].gt(segment).alias('airborne')
        )

        change_idx = (
            frame['airborne'].shift(1) != frame['airborne']
        ).fill_null(True).to_numpy().nonzero()[0]

        boundaries = list(change_idx) + [len(frame)]

        subframes = [
            frame.slice(start, stop - start) for start, stop in zip(boundaries, boundaries[1:])
        ]

        u.lg.info(
            f'Segmented into {len(subframes)} frames by height {segment} meters'
        )

        result_frames.extend(subframes)

    metaproc.update({
        'segment_height_meters': segment,
        'segment_height_in': len(frames),
        'segment_height_out': len(result_frames),
    })

    return result_frames


def segment_by_idle(frames, params: SegmentParams, metaproc: dict):
    idle_time_milliseconds = params['idle_time_seconds'] * 1000.0

    u.lg.info(
        f'Segmenting by idle time {idle_time_milliseconds} milliseconds'
    )

    result_frames = []

    for frame in frames:
        ts = frame['timestamp'].to_numpy()
        diffs = ts[1:] - ts[:-1]
        split_indices = (diffs > idle_time_milliseconds).nonzero()[0] + 1
        indices = [0] + split_indices.tolist() + [len(frame)]

        for start, end in zip(indices[:-1], indices[1:]):
            subframe = frame.slice(start, end - start)
            result_frames.append(subframe)

    metaproc.update({
        'segment_idle_time_ms': idle_time_milliseconds,
        'segment_idle_time_in': len(frames),
        'segment_idle_time_out': len(result_frames),
    })

    return result_frames


def filter_duration(frames, params: SegmentParams, metaproc: dict):
    duration = params['filter_duration_seconds'] * 1000.0
    u.lg.info(f'Filtering by duration {duration} milliseconds')

    result_frames = [
        frame for frame in frames
        if frame['timestamp'].max() - frame['timestamp'].min() > duration
    ]

    u.lg.info(f'Filtered to {len(result_frames)} frames')

    metaproc.update({
        'filter_duration_ms': duration,
        'filter_duration_in': len(frames),
        'filter_duration_out': len(result_frames),
    })

    return result_frames


def segment(
    dataset: FlightlogDataset,
    params: SegmentParams,
):
    frames = dataset.frames
    metaproc = {}

    if params['segment_by_height']:
        frames = segment_airborne(frames, params, metaproc)

    if params['segment_by_idle']:
        frames = segment_by_idle(frames, params, metaproc)

    if params['filter_by_duration']:
        frames = filter_duration(frames, params, metaproc)

    result_dataset = dataset.evolve(frames=frames, metadata={
        'segment_by_height': params['segment_by_height'],
        'segment_by_idle': params['segment_by_idle'],
        'filter_by_duration': params['filter_by_duration'],
    })

    metaproc.update({
        'num_frames': len(result_dataset.frames),
    })

    return result_dataset, metaproc
