import json
from datetime import datetime, UTC

from toolz.itertoolz import accumulate, last
from pygeodesy.dms import latDMS, lonDMS, F_DMS

from fvc.df.util import JsonlinesIO


def stats(args, io: JsonlinesIO):
    metadata = io.read()

    if not metadata:
        raise UserWarning('No metadata found')

    if (content := metadata.get('content')) != 'flightlog':
        raise UserWarning(f'Unsupported content type: {content}')

    def iterate():
        while data := io.read():
            yield data

    targets = {
        'time': lambda rec: rec['time']['unix'],
        'lat': lambda rec: rec['pos']['loc']['lat'],
        'lon': lambda rec: rec['pos']['loc']['lon'],
        'alt': lambda rec: rec['pos']['loc']['alt']
    }

    init = {
        key: {
            'min': float('inf'),
            'max': float('-inf')
        }
        for key in targets.keys()
    }

    def stat_acc(stats, rec):
        for key, fetch in targets.items():
            stats[key]['min'] = min(stats[key]['min'], fetch(rec))
            stats[key]['max'] = max(stats[key]['max'], fetch(rec))

        return stats

    stats = last(accumulate(stat_acc, iterate(), initial=init))  # type: ignore

    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        def ftime(ts):
            return datetime.fromtimestamp(ts/1000.0, tz=UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

        def flat(lat):
            return latDMS(lat, form=F_DMS)

        def flon(lon):
            return lonDMS(lon, form=F_DMS)

        print(f'Start: {ftime(stats["time"]["min"])}')
        print(f'End: {ftime(stats["time"]["max"])}')

        print(f'From latutude {flat(stats["lat"]["min"])} to {flat(stats["lat"]["max"])}')
        print(f'From longitude {flon(stats["lon"]["min"])} to {flon(stats["lon"]["max"])}')
        print(f'From altitude {stats["alt"]["min"]:.2f} to {stats["alt"]["max"]:.2f}')
