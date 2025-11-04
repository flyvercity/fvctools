from pathlib import Path
from typing import TypedDict

import polars as pl

import fvc.tools.df.utils as u


class SegmentParams(TypedDict):
    input_path: Path
    vdim: str = 'alt'
    verbose: bool = False
    segment_by_height: bool = False
    segment_height_meters: float
    segment_by_idle: bool = False
    segment_idle_time_seconds: float
    filter_by_duration: bool = False
    filter_duration_seconds: float


def load_frame(params: SegmentParams):
    """ Parameters:
        - input_path: Path to the FVC data file
    """
    input_path = u.input_path(params)
    dataset = u.FvcDataset.read(input_path)

    if dataset.metadata.get('content') != 'flightlog':
        raise UserWarning(f'File {input_path} is not a flightlog')

    df = dataset.df

    if params.get('verbose'):
        u.lg.info(f'Loaded {len(df)} rows')
        print(df)

    df = df.with_columns(
        pl.col('time').struct.field('unix').alias('timestamp'),
    )

    return df.sort('timestamp')


def segment_airborne(frames, params: SegmentParams, metadata: dict):
    segment = params['segment_height_meters']
    vdim = params['vdim']

    result_frames = []

    for frame in frames:
        u.lg.info(f'Segmenting by height {segment} meters')
        u.lg.info(f'Using vertical dimension: {vdim}')

        frame = frame.with_columns(
            pl.col('pos').struct.field('loc').struct.field(vdim).alias('vdim')
        )

        frame = frame.filter(
            pl.col('vdim').is_not_null()
        )

        frame = frame.with_columns(
            frame['vdim'].gt(segment).alias('airborne')
        )

        change_idx = (frame['airborne'].shift(1) != frame['airborne']).fill_null(True).to_numpy().nonzero()[0]

        boundaries = list(change_idx) + [len(frame)]

        subframes = [
            frame.slice(start, stop - start) for start, stop in zip(boundaries, boundaries[1:])
        ]

        u.lg.info(
            f'Segmented into {len(subframes)} frames by height {segment} meters'
        )

        result_frames.extend(subframes)

    metadata.update({
        'segment_height_meters': segment,
        'segment_height_in': len(frames),
        'segment_height_out': len(result_frames),
    })

    return result_frames


def segment_by_idle(frames, params: SegmentParams, metadata: dict):
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

    metadata.update({
        'segment_idle_time_ms': idle_time_milliseconds,
        'segment_idle_time_in': len(frames),
        'segment_idle_time_out': len(result_frames),
    })

    return result_frames


def filter_duration(frames, params: SegmentParams, metadata: dict):
    duration = params['filter_duration_seconds'] * 1000.0
    u.lg.info(f'Filtering by duration {duration} milliseconds')

    result_frames = [
        frame for frame in frames
        if frame['timestamp'].max() - frame['timestamp'].min() > duration
    ]

    u.lg.info(f'Filtered to {len(result_frames)} frames')

    metadata.update({
        'filter_duration_ms': duration,
        'filter_duration_in': len(frames),
        'filter_duration_out': len(result_frames),
    })

    return result_frames


def segment(params: SegmentParams):
    frames = [load_frame(params)]
    metadata = {}

    if params['segment_by_height']:
        if params.get('vdim') is None:
            raise UserWarning('Segmentation requires a vertical dimension')

        frames = segment_airborne(frames, params, metadata)

    if params['segment_by_idle']:
        frames = segment_by_idle(frames, params, metadata)

    if params['filter_by_duration']:
        frames = filter_duration(frames, params, metadata)

    return frames, metadata
