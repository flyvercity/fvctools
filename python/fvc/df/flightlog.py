import json
from datetime import datetime, UTC

from toolz.itertoolz import accumulate, last
from pygeodesy.dms import latDMS, lonDMS, F_DMS

from fvc.df.util import JsonlinesIO


def stats(params, io: JsonlinesIO):
    metadata = io.read()

    if not metadata:
        raise UserWarning('No metadata found')

    if (content := metadata.get('content')) != 'flightlog':
        raise UserWarning(f'Unsupported content type: {content}')

    def fetch_loc(field):
        def inner(rec):
            pos = rec['pos']
            return pos['loc'][field] if 'loc' in pos else None

        return inner

    targets = {
        'time': lambda rec: rec['time']['unix'],
        'lat': fetch_loc('lat'),
        'lon': fetch_loc('lon'),
        'alt': fetch_loc('alt')
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
            if val := fetch(rec):
                stats[key]['min'] = min(stats[key]['min'], val)
                stats[key]['max'] = max(stats[key]['max'], val)

        return stats

    stats = last(accumulate(stat_acc, io.iterate(), initial=init))  # type: ignore

    if params['JSON']:
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
