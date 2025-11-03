from datetime import UTC, datetime

import polars as pl
from pygeodesy.dms import F_DMS, latDMS, lonDMS
import rich

import fvc.tools.df.utils as u


def load_frame(params):
    """ Parameters:
        - input_path: Path to the FVC data file
    """
    input_path = u.input_path(params)
    dataset = u.FvcDataset.read(input_path)

    if dataset.metadata.get('content') != 'flightlog':
        raise UserWarning(f'File {input_path} is not a flightlog')

    df = dataset.df.select(
        pl.col('time').struct.field('unix').alias('time'),
        pl.col('pos').struct.field('loc').struct.field('lat').alias('lat'),
        pl.col('pos').struct.field('loc').struct.field('lon').alias('lon'),
        pl.col("pos").struct.field("loc").struct.field("alt").is_not_null()
    )

    return df.sort('time')


def segment_airborne(df, segment: str):
    df = df.filter(pl.col('alt').is_not_null())
    df = df.with_columns(df['alt'].lt(float(segment)).alias('on_ground'))

    change_idx = (df['on_ground'].shift(1) != df['on_ground']).fill_null(True).to_numpy().nonzero()[0]

    boundaries = list(change_idx) + [len(df)]

    frames = [df.slice(start, stop - start) for start, stop in zip(boundaries, boundaries[1:])]

    u.lg.info(f'Segmented into {len(frames)} frames')

    return frames


def calculate_stats(df):
    df = df.with_columns(df['time'].diff().alias('time_diff'))

    stats = {
        'time': {
            'min': df['time'].min(),
            'max': df['time'].max(),
        },
        'duration': df['time'].max() - df['time'].min(),
        'lon': {
            'min': df['lon'].min(),
            'max': df['lon'].max(),
        },
        'lat': {
            'min': df['lat'].min(),
            'max': df['lat'].max(),
        },
        'time_diff': {
            'min': df['time_diff'].min(),
            'max': df['time_diff'].max(),
        },
    }

    df_alt = df.filter(pl.col('alt').is_not_null())
        
    if not df_alt.is_empty():
        stats['alt'] = {
            'min': df_alt['alt'].min(),
            'max': df_alt['alt'].max(),
        }

    if 'on_ground' in df.columns:
        stats['on_ground'] = df[0]['on_ground'].to_list()[0]

    return stats


def print_stats(params):
    df = load_frame(params)

    if segment := params.get('segment'):
        frames = segment_airborne(df, segment=segment)
    else:
        frames = [df]

    for frame in frames:
        stats = calculate_stats(frame)
        _print_stats(stats)


def _print_stats(stats):
    def ftime(ts):
        return datetime.fromtimestamp(ts / 1000.0, tz=UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

    def flat(lat):
        return latDMS(lat, form=F_DMS)

    def flon(lon):
        return lonDMS(lon, form=F_DMS)

    rich.print('-' * 60)

    if 'on_ground' in stats:
        rich.print(f'On ground: {stats["on_ground"]}')

    rich.print(f'Start: {ftime(stats["time"]["min"])}')
    rich.print(f'End: {ftime(stats["time"]["max"])}')
    rich.print(f'Duration: {stats["duration"] / 1000.0:.2f} seconds')

    rich.print(f'From latutude {flat(stats["lat"]["min"])} to {flat(stats["lat"]["max"])}')
    rich.print(f'From longitude {flon(stats["lon"]["min"])} to {flon(stats["lon"]["max"])}')
    rich.print(f'From altitude {stats["alt"]["min"]:.2f} to {stats["alt"]["max"]:.2f}')
    rich.print(f'Time difference: {stats["time_diff"]["min"]} to {stats["time_diff"]["max"]}')
    rich.print('-' * 60)
