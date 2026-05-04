from datetime import UTC, datetime
from typing import Optional

from fvc.tools.flightlog.load import FlightlogDataset
import polars as pl
from pygeodesy.dms import F_DMS, latDMS, lonDMS
import rich

from fvc.tools.utils import plnested


def calculate_segment_stats(index: int, df: pl.DataFrame, vdim: Optional[str] = None):
    projection = df.select(
        plnested('time.unix').alias('time'),
        plnested('pos.loc.lon').alias('lon'),
        plnested('pos.loc.lat').alias('lat'),
    )
    time_diff = projection['time'].diff().drop_nulls()

    stats = {
        'index': index,
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

    if vdim is not None:
        vdim_projection = df.select(plnested(vdim).alias(vdim))

        stats['vdim'] = {
            'name': vdim,
            'min': vdim_projection[vdim].min(),
            'max': vdim_projection[vdim].max(),
        }

    return stats


def calculate_flightlog_stats(dataset: FlightlogDataset, vdim: Optional[str] = None) -> dict:
    frames = dataset.frames

    segment_stats = [calculate_segment_stats(inx, frame, vdim=vdim) for inx, frame in enumerate(frames)]

    stats = {
        'time': {
            'min': min(stat['time']['min'] for stat in segment_stats),
            'max': max(stat['time']['max'] for stat in segment_stats),
        },
        'time-iso': {
            'min': datetime.fromtimestamp(
                min(stat['time']['min'] for stat in segment_stats) / 1000.0, tz=UTC
            ).isoformat(),
            'max': datetime.fromtimestamp(
                max(stat['time']['max'] for stat in segment_stats) / 1000.0, tz=UTC
            ).isoformat(),
        },
        'duration': max(stat['duration'] for stat in segment_stats),
        'duration-hours': max(stat['duration'] for stat in segment_stats) / 1000.0 / 3600.0,
        'lon': {
            'min': min(stat['lon']['min'] for stat in segment_stats),
            'max': max(stat['lon']['max'] for stat in segment_stats),
        },
        'lat': {
            'min': min(stat['lat']['min'] for stat in segment_stats),
            'max': max(stat['lat']['max'] for stat in segment_stats),
        },
        vdim: {
            'min': min(stat['vdim']['min'] for stat in segment_stats),
            'max': max(stat['vdim']['max'] for stat in segment_stats),
        },
    }

    return stats


def print_stats(frames: list[pl.DataFrame], vdim: Optional[str] = None):
    stats = calculate_flightlog_stats(frames, vdim=vdim)

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

    rich.print(f'From latutude {flat(stats["lat"]["min"])} to {flat(stats["lat"]["max"])}')

    rich.print(f'From longitude {flon(stats["lon"]["min"])} to {flon(stats["lon"]["max"])}')

    rich.print(f'Time difference: {stats["time_diff"]["min"]} to {stats["time_diff"]["max"]}')

    if 'vdim' in stats:
        rich.print(f'From {stats["vdim"]["name"]} {stats["vdim"]["min"]:.2f} to {stats["vdim"]["max"]:.2f}')

    rich.print('-' * 60)
