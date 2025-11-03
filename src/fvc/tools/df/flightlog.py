from datetime import UTC, datetime

import polars as pl
from pygeodesy.dms import F_DMS, latDMS, lonDMS
from rich.live import Live
from rich.spinner import Spinner
import rich

import fvc.tools.df.utils as u


def stats(params):
    input_path = u.input_path(params)

    with Live(
        Spinner('aesthetic', 'Analyzing...'),
        transient=True,
    ):
        dataset = u.FvcDataset.read(input_path)

        if dataset.metadata.get('content') != 'flightlog':
            raise UserWarning(f'File {input_path} is not a flightlog')

        df = dataset.df
        df = df.select(
            pl.col('time').struct.field('unix').alias('time'),
            pl.col('pos').struct.field('loc').struct.field('lat').alias('lat'),
            pl.col('pos').struct.field('loc').struct.field('lon').alias('lon'),
            pl.col('pos').struct.field('loc').struct.field('alt').alias('alt'),
        )

        diff = df['time'].diff().alias('time_diff')
        df = df.with_columns(diff)

        stats = {
            'time': {
                'min': df['time'].min(),
                'max': df['time'].max(),
            },
            'lon': {
                'min': df['lon'].min(),
                'max': df['lon'].max(),
            },
            'lat': {
                'min': df['lat'].min(),
                'max': df['lat'].max(),
            },
            'alt': {
                'min': df['alt'].min(),
                'max': df['alt'].max(),
            },
            'time_diff': {
                'min': df['time_diff'].min(),
                'max': df['time_diff'].max(),
            },
        }

        if params['JSON']:
            u.json_print(params, stats)
        else:
            _print_stats(stats)


def _print_stats(stats):
    def ftime(ts):
        return datetime.fromtimestamp(ts / 1000.0, tz=UTC).strftime(
            '%Y-%m-%d %H:%M:%S UTC'
        )

    def flat(lat):
        return latDMS(lat, form=F_DMS)

    def flon(lon):
        return lonDMS(lon, form=F_DMS)

    rich.print(f'Start: {ftime(stats["time"]["min"])}')
    rich.print(f'End: {ftime(stats["time"]["max"])}')

    rich.print(
        f'From latutude {flat(stats["lat"]["min"])} to {flat(stats["lat"]["max"])}'
    )
    rich.print(
        f'From longitude {flon(stats["lon"]["min"])} to {flon(stats["lon"]["max"])}'
    )
    rich.print(
        f'From altitude {stats["alt"]["min"]:.2f} to {stats["alt"]["max"]:.2f}'
    )
    rich.print(
        f'Time difference: {stats["time_diff"]["min"]} to {stats["time_diff"]["max"]}'
    )
