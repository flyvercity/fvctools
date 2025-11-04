from pathlib import Path
from typing import TypedDict

import polars as pl

import fvc.tools.df.utils as u


class SegmentParams(TypedDict):
    verbose: bool
    input_path: Path
    vdim: str
    segment_by_altitude: bool
    segment_altitude_meters: float
    filter_by_duration: bool
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


def segment_airborne(df, params: SegmentParams):
    segment = params['segment_altitude_meters']
    vdim = params['vdim']
    u.lg.info(f'Segmenting by altitude {segment} meters')
    u.lg.info(f'Using vertical dimension: {vdim}')

    df = df.with_columns(
        pl.col('pos').struct.field('loc').struct.field(vdim).alias('vdim')
    )

    df = df.filter(
        pl.col('vdim').is_not_null()
    )

    df = df.with_columns(
        df['vdim'].gt(segment).alias('airborne')
    )

    change_idx = (df['airborne'].shift(1) != df['airborne']).fill_null(True).to_numpy().nonzero()[0]

    boundaries = list(change_idx) + [len(df)]

    frames = [df.slice(start, stop - start) for start, stop in zip(boundaries, boundaries[1:])]

    u.lg.info(f'Segmented into {len(frames)} frames by altitude {segment} meters')

    return frames


def filter_duration(frames, params):
    duration = params['filter_duration_seconds'] * 1000.0
    u.lg.info(f'Filtering by duration {duration} milliseconds')

    frames = [
        frame for frame in frames
        if frame['timestamp'].max() - frame['timestamp'].min() > duration
    ]

    u.lg.info(f'Filtered to {len(frames)} frames')
    return frames


def segment(params: SegmentParams):
    df = load_frame(params)

    if params.get('segment_by_altitude'):
        if params.get('vdim') is None:
            raise UserWarning('Segmentation requires a vertical dimension')

        frames = segment_airborne(df, params)
    else:
        frames = [df]

    if params['filter_by_duration']:
        frames = filter_duration(frames, params)

    return frames
