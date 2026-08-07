from datetime import UTC, datetime
from typing import Optional

from fvc.tools.flightlog.load import FlightlogDataset
import polars as pl
from pygeodesy.dms import F_DMS, latDMS, lonDMS
import rich

from fvc.tools.utils import plnested


def _scalar(value):
    """Convert Polars scalar to plain Python type."""
    if hasattr(value, 'item'):
        return value.item()
    return value


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
            'min': _scalar(projection['time'].min()),
            'max': _scalar(projection['time'].max()),
        },
        'duration': _scalar(projection['time'].max() - projection['time'].min()),
        'lon': {
            'min': _scalar(projection['lon'].min()),
            'max': _scalar(projection['lon'].max()),
        },
        'lat': {
            'min': _scalar(projection['lat'].min()),
            'max': _scalar(projection['lat'].max()),
        },
        'time_diff': {
            'min': _scalar(time_diff.min()),
            'max': _scalar(time_diff.max()),
        },
    }

    if vdim is not None:
        vdim_projection = df.select(plnested(vdim).alias(vdim))

        stats['vdim'] = {
            'name': vdim,
            'min': _scalar(vdim_projection[vdim].min()),
            'max': _scalar(vdim_projection[vdim].max()),
        }

    return stats


def calculate_flightlog_stats(dataset: FlightlogDataset, vdim: Optional[str] = None) -> dict:
    frames = dataset.frames

    if not frames:
        return {
            'num_segments': 0,
            'empty': True,
        }

    segment_stats = [calculate_segment_stats(inx, frame, vdim=vdim) for inx, frame in enumerate(frames)]

    total_duration = sum(stat['duration'] for stat in segment_stats)

    stats = {
        'num_segments': len(segment_stats),
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
        'total_duration': total_duration,
        'total_duration_hours': total_duration / 1000.0 / 3600.0,
        'max_segment_duration': max(stat['duration'] for stat in segment_stats),
        'max_segment_duration_hours': max(stat['duration'] for stat in segment_stats) / 1000.0 / 3600.0,
        'time_diff': {
            'min': min(stat['time_diff']['min'] for stat in segment_stats),
            'max': max(stat['time_diff']['max'] for stat in segment_stats),
        },
        'lon': {
            'min': min(stat['lon']['min'] for stat in segment_stats),
            'max': max(stat['lon']['max'] for stat in segment_stats),
        },
        'lat': {
            'min': min(stat['lat']['min'] for stat in segment_stats),
            'max': max(stat['lat']['max'] for stat in segment_stats),
        },
    }

    if vdim is not None:
        stats[vdim] = {
            'min': min(stat['vdim']['min'] for stat in segment_stats),
            'max': max(stat['vdim']['max'] for stat in segment_stats),
        }

    return stats


def print_stats(dataset: FlightlogDataset, vdim: Optional[str] = None):
    result = calculate_flightlog_stats(dataset, vdim=vdim)

    if result.get('empty'):
        rich.print('No segments to display.')
        return

    def ftime(ts):
        return datetime.fromtimestamp(ts / 1000.0, tz=UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

    def flat(lat):
        return latDMS(lat, form=F_DMS)

    def flon(lon):
        return lonDMS(lon, form=F_DMS)

    rich.print('-' * 60)

    rich.print(f'Segments: {result["num_segments"]}')
    rich.print(f'Start: {ftime(result["time"]["min"])}')
    rich.print(f'End: {ftime(result["time"]["max"])}')
    rich.print(f'Total duration: {result["total_duration"] / 1000.0:.2f} seconds')
    rich.print(f'Max segment duration: {result["max_segment_duration"] / 1000.0:.2f} seconds')

    rich.print(f'From latitude {flat(result["lat"]["min"])} to {flat(result["lat"]["max"])}')
    rich.print(f'From longitude {flon(result["lon"]["min"])} to {flon(result["lon"]["max"])}')

    rich.print(f'Time difference: {result["time_diff"]["min"]} to {result["time_diff"]["max"]}')

    if vdim and vdim in result:
        rich.print(f'From {vdim} {result[vdim]["min"]:.2f} to {result[vdim]["max"]:.2f}')

    rich.print('-' * 60)
