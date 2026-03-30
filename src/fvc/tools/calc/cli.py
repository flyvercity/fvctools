from datetime import UTC, datetime

import click

import fvc.tools.utils as u
import fvc.tools.calc.terrain as terrain
import fvc.tools.calc.geoid as geoid
from fvc.tools.calc.utils import lg


@click.group(help='Specialized calculation tools')
def calc():
    pass


@calc.command(
    name='epoch',
    help='Convert UNIX timestamps to human-readable format',
)
@click.pass_obj
@click.option(
    '--nanoseconds',
    is_flag=True,
    help='Use nanoseconds instead of milliseconds',
)
@click.argument('epoch', type=int, required=True)
def epoch_command(params, epoch, nanoseconds):
    if nanoseconds:
        dt = datetime.fromtimestamp(epoch / 1_000_000_000.0, UTC)
    else:
        dt = datetime.fromtimestamp(epoch / 1000.0, UTC)

    if not params['JSON']:
        print(dt.isoformat())
    else:
        u.json_print(params, {'datetime': dt.isoformat()})


@calc.command(
    name='undulation',
    help='Get geoid indulation by latitude/longitude',
)
@click.pass_obj
@click.argument('latitude', type=str)
@click.argument('longitude', type=str)
def undulation_command(obj, latitude, longitude):
    pgm = geoid.load_geoid(obj)

    u.lg.debug(f'Given {latitude} {longitude}')

    lat = u.parse_lat(latitude)
    lon = u.parse_lon(longitude)

    lg.debug(f'Using {u.render_latlon(lat, lon)}')

    geoid_height = pgm.height(lat, lon)

    if not obj['JSON']:
        print(geoid_height)
    else:
        u.json_print(obj, {'undulation': geoid_height})


@calc.command(name='terrain', help='Get terrain elevation by latitude/longitude and undulation or ellipsoid height')
@click.pass_obj
@click.option(
    '--normal',
    is_flag=True,
    help='Use undulation instead of ellipsoid height',
)
@click.option(
    '--copernicus-dir',
    type=str,
    help='Directory containing Copernicus DEM files',
)
@click.argument('lat', type=str)
@click.argument('lon', type=str)
@click.argument('geo-amsl-height', type=float)
def terrain_command(obj, lat, lon, normal, geo_amsl_height, copernicus_dir):
    lat = u.parse_lat(lat)
    lon = u.parse_lon(lon)

    if normal:
        amsl_height = geo_amsl_height
    else:
        pgm = geoid.load_geoid(obj)
        amsl_height = geoid.ellipsoid_to_amsl(pgm, lat, lon, geo_amsl_height)

    lg.debug(f'Given {lat} {lon} {amsl_height} ({geo_amsl_height} AMSL={normal})')

    with terrain.Terrain(copernicus_dir) as t:
        terrain_height = t.height(lat, lon, amsl_height)

    if not obj['JSON']:
        print(terrain_height)
    else:
        u.json_print(obj, {'terrain': terrain_height})
