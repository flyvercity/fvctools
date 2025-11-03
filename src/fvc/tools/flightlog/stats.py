from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, TypedDict

import polars as pl
from pygeodesy.dms import F_DMS, latDMS, lonDMS
import rich

import fvc.tools.df.utils as u


class StatsParams(TypedDict):
    verbose: bool
    input_path: Path
    vdim: str
    segment: float


def load_frame(params: StatsParams):
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


def segment_airborne(df, params: StatsParams):
    segment = float(params['segment'])
    vdim = params['vdim']

    df = df.with_columns(
        pl.col('pos').struct.field('loc').struct.field(vdim).alias('vdim')
    )

    df = df.filter(
        pl.col('vdim').is_not_null()
    )

    df = df.with_columns(
        df['vdim'].gt(float(segment)).alias('airborne')
    )

    change_idx = (df['airborne'].shift(1) != df['airborne']).fill_null(True).to_numpy().nonzero()[0]

    boundaries = list(change_idx) + [len(df)]

    frames = [df.slice(start, stop - start) for start, stop in zip(boundaries, boundaries[1:])]

    u.lg.info(f'Segmented into {len(frames)} frames')

    return frames


def calculate_stats(df, vdim: Optional[str] = None):
    projection = df.select(
        pl.col('time').struct.field('unix').alias('time'),
        pl.col('pos').struct.field('loc').struct.field('lon').alias('lon'),
        pl.col('pos').struct.field('loc').struct.field('lat').alias('lat'),
    )
    time_diff = projection['time'].diff().drop_nulls()

    stats = {
        'time': {
            'min': projection['time'].min(),
            'max': projection['time'].max(),
        },
        'duration': projection['time'].max() - projection['time'].min(),
        'lon': {
            'min': projection['lon'].min(),
            'max': projection['lon'].max(),
        },
        'lat': {
            'min': projection['lat'].min(),
            'max': projection['lat'].max(),
        },
        'time_diff': {
            'min': time_diff.min(),
            'max': time_diff.max(),
        },
    }

    u.lg.info(f'Using vertical dimension: {vdim}')

    if vdim is not None:
        vdim_projection = df.select(
            pl.col('pos').struct.field('loc').struct.field(vdim).alias(vdim)
        )

        stats['vdim'] = {
            'name': vdim,
            'min': vdim_projection[vdim].min(),
            'max': vdim_projection[vdim].max(),
        }

    if 'airborne' in df.columns:
        stats['airborne'] = df[0]['airborne'].to_list()[0]

    return stats


def print_stats(params: StatsParams):
    """ P
    Parameters:
        - input_path: Path to the FVC data file
        - vdim: Visualize dimension
        - segment: Segment altitude
    """
    df = load_frame(params)

    if params.get('segment') is not None:
        if params.get('vdim') is None:
            raise UserWarning('Segmentation requires a vertical dimension')

        frames = segment_airborne(df, params)
    else:
        frames = [df]

    for frame in frames:
        stats = calculate_stats(frame, vdim=params.get('vdim'))
        _print_stats(stats)


def _print_stats(stats: dict):
    def ftime(ts):
        return datetime.fromtimestamp(ts / 1000.0, tz=UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

    def flat(lat):
        return latDMS(lat, form=F_DMS)

    def flon(lon):
        return lonDMS(lon, form=F_DMS)

    rich.print('-' * 60)

    if 'airborne' in stats:
        rich.print(f'Airborne: {stats["airborne"]}')

    rich.print(f'Start: {ftime(stats["time"]["min"])}')
    rich.print(f'End: {ftime(stats["time"]["max"])}')
    rich.print(f'Duration: {stats["duration"] / 1000.0:.2f} seconds')

    rich.print(
        f'From latutude {flat(stats["lat"]["min"])} to {flat(stats["lat"]["max"])}'
    )

    rich.print(
        f'From longitude {flon(stats["lon"]["min"])} to {flon(stats["lon"]["max"])}'
    )

    rich.print(
        f'Time difference: {stats["time_diff"]["min"]} to {stats["time_diff"]["max"]}'
    )

    if 'vdim' in stats:
        rich.print(
            f'From {stats["vdim"]["name"]} {stats["vdim"]["min"]:.2f} to {stats["vdim"]["max"]:.2f}'
        )

    rich.print('-' * 60)
