import click
from datetime import datetime
import logging as lg

import fvc.tools.util as u
import fvc.tools.df.util as df_u


@click.group(help='Specialized calculation tools')
def calc():
    pass


@calc.command(help='Convert UNIX timestamps to human-readable format')
@click.pass_obj
@click.argument('epoch', type=int, required=True)
def epoch(params, epoch):
    dt = datetime.fromtimestamp(epoch / 1000.0)
    
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
