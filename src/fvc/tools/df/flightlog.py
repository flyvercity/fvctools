import json
from datetime import UTC, datetime

from benedict import benedict
from pygeodesy.dms import F_DMS, latDMS, lonDMS
from toolz.itertoolz import accumulate, last
from rich.progress import Progress
import rich

import fvc.tools.df.utils as u


def stats(params):
    input_path = u.input_path(params)

    with Progress(transient=True) as progress:
        total_size = input_path.stat().st_size
        task = progress.add_task('Analyzing...', total=total_size)

        def callback(s):
            progress.update(task, advance=s)

        with u.JsonlinesIO(input_path, 'r', callback=callback) as io:
            metadata = io.read()

            if not metadata:
                raise UserWarning('No metadata found')

            if (content := metadata.get('content')) != 'flightlog':
                raise UserWarning(f'Unsupported content type: {content}')

            targets = [
                'time.unix',
                'pos.loc.lat',
                'pos.loc.lon',
                'pos.loc.alt',
            ]

            init = {
                key: {'min': float('inf'), 'max': float('-inf')}
                for key in targets
            }

            def stat_acc(stats, rec: benedict):
                for key in targets:
                    if val := rec.get_float(key):
                        stats[key]['min'] = min(stats[key]['min'], val)
                        stats[key]['max'] = max(stats[key]['max'], val)

                return stats

            stats = last(accumulate(stat_acc, io.iterate(), initial=init))

            if params['JSON']:
                print(json.dumps(stats, indent=2))
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

    rich.print(f'Start: {ftime(stats["time.unix"]["min"])}')
    rich.print(f'End: {ftime(stats["time.unix"]["max"])}')

    rich.print(
        f'From latutude {flat(stats["pos.loc.lat"]["min"])} to {flat(stats["pos.loc.lat"]["max"])}'
    )
    rich.print(
        f'From longitude {flon(stats["pos.loc.lon"]["min"])} to {flon(stats["pos.loc.lon"]["max"])}'
    )
    rich.print(
        f'From altitude {stats["pos.loc.alt"]["min"]:.2f} to {stats["pos.loc.alt"]["max"]:.2f}'
    )
