import click
from datetime import datetime, UTC
import logging as lg

import fvc.tools.util as u


@click.group(help='Specialized calculation tools')
def calc():
    pass


@calc.command(help='Convert UNIX timestamps to human-readable format')
@click.pass_obj
@click.option('--nanoseconds', is_flag=True, help='Use nanoseconds instead of milliseconds')
@click.argument('epoch', type=int, required=True)
def epoch(params, epoch, nanoseconds):
    if nanoseconds:
        dt = datetime.fromtimestamp(epoch / 1_000_000_000.0, UTC)
    else:
        dt = datetime.fromtimestamp(epoch / 1000.0, UTC)

    if not params['JSON']:
        print(dt.isoformat())
    else:
        u.json_print(params, {'datetime': dt.isoformat()})


@calc.command(help='Get geoid indulation by latitude/longitude')
@click.pass_obj
@click.argument('latitude', type=str)
@click.argument('longitude', type=str)
def undulation(params, latitude, longitude):
    geoid = u.load_geoid(params)

    lg.debug(f'Given {latitude} {longitude}')

    lat = u.parse_lat(latitude)
    lon = u.parse_lon(longitude)

    lg.debug(f'Using {u.render_latlon(lat, lon)}')

    height = geoid.height(lat, lon)

    if not params['JSON']:
        print(height)
    else:
        u.json_print(params, {'undulation': height})
