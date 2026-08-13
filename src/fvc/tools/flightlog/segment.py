import math
import os
from pathlib import Path
from typing import TypedDict

import polars as pl

import fvc.tools.df.utils as dfu
from fvc.tools.flightlog.load import FlightlogDataset
from fvc.tools.utils import plnested


class SegmentParams(TypedDict):
    segment_by_height: bool
    segment_height_meters: float
    airborne_only: bool
    segment_by_idle: bool
    idle_time_seconds: float
    filter_by_duration: bool
    filter_duration_seconds: float
    filter_by_displacement: bool
    filter_displacement_lateral_meters: float
    filter_displacement_vertical_meters: float


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

        frames = [frame.drop('airborne') for frame in frames]

    _dump(dump_steps, 'airborne', frames)

    if params['segment_by_idle']:
        frames = segment_by_idle(frames, params, metaproc)

    _dump(dump_steps, 'idle', frames)

    if params['filter_by_duration']:
        frames = filter_duration(frames, params, metaproc)

    _dump(dump_steps, 'duration', frames)

    if params['filter_by_displacement']:
        frames = filter_displacement(frames, params, metaproc)

    _dump(dump_steps, 'displacement', frames)

    result_dataset = dataset.evolve(
        frames=frames,
        metadata={
            'segment_by_height': params['segment_by_height'],
            'segment_by_idle': params['segment_by_idle'],
            'filter_by_duration': params['filter_by_duration'],
            'filter_by_displacement': params['filter_by_displacement'],
            'filter_displacement_lateral_meters': params['filter_displacement_lateral_meters'],
            'filter_displacement_vertical_meters': params['filter_displacement_vertical_meters'],
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
        null_count = frame['derived_height'].null_count()

        if null_count > 0:
            raise ValueError(
                f'derived_height contains {null_count} null values '
                f'({null_count}/{frame.height} rows). '
                f'Nulls must be resolved by the cleanup step before segmentation.'
            )

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


def segment_by_timestamp(frames: list[pl.DataFrame], step_ms: float):
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

    result_frames = [frame for frame in frames if frame['timestamp'].max() - frame['timestamp'].min() >= duration]

    dfu.lg.info(f'Filtered to {len(result_frames)} frames')

    metaproc.update(
        {
            'filter_duration_ms': duration,
            'filter_duration_in': len(frames),
            'filter_duration_out': len(result_frames),
        }
    )

    return result_frames


def filter_displacement(frames, params: SegmentParams, metaproc: dict):
    lateral_threshold = params['filter_displacement_lateral_meters']
    vertical_threshold = params['filter_displacement_vertical_meters']

    dfu.lg.info(
        f'Filtering by displacement: lateral >= {lateral_threshold}m '
        f'or vertical >= {vertical_threshold}m'
    )

    result_frames = []

    for frame in frames:
        if frame.is_empty():
            continue

        stats = frame.select(
            plnested('pos.loc.lat').min().alias('min_lat'),
            plnested('pos.loc.lat').max().alias('max_lat'),
            plnested('pos.loc.lon').min().alias('min_lon'),
            plnested('pos.loc.lon').max().alias('max_lon'),
            pl.col('derived_height').min().alias('min_h'),
            pl.col('derived_height').max().alias('max_h'),
        ).to_dicts()[0]

        min_lat = stats['min_lat']
        max_lat = stats['max_lat']
        min_lon = stats['min_lon']
        max_lon = stats['max_lon']
        min_h = stats['min_h']
        max_h = stats['max_h']

        if min_lat is None or max_lat is None or min_lon is None or max_lon is None:
            continue

        mean_lat_rad = math.radians((min_lat + max_lat) / 2.0)
        lat_span_m = (max_lat - min_lat) * 111_320
        lon_span_m = (max_lon - min_lon) * 111_320 * math.cos(mean_lat_rad)
        lateral = math.hypot(lat_span_m, lon_span_m)

        vertical = 0.0
        if min_h is not None and max_h is not None:
            vertical = max_h - min_h

        if lateral >= lateral_threshold or vertical >= vertical_threshold:
            result_frames.append(frame)

    dfu.lg.info(f'Displacement filter: {len(frames)} -> {len(result_frames)} frames')

    metaproc.update({
        'filter_displacement_lateral_meters': lateral_threshold,
        'filter_displacement_vertical_meters': vertical_threshold,
        'filter_displacement_in': len(frames),
        'filter_displacement_out': len(result_frames),
    })

    return result_frames


DUMP_DIR = Path(os.getenv('FVC_DUMP_DIR', '.tmp'))


def _dump(dump_steps: bool, step: str, frames: list[pl.DataFrame]):
    if dump_steps:
        DUMP_DIR.mkdir(parents=True, exist_ok=True)
        for inx, frame in enumerate(frames):
            frame.write_ndjson(DUMP_DIR / f'dump_segment_{step}_{inx}')
