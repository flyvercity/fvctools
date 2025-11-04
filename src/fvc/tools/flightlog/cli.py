import click

from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress

import fvc.tools.flightlog.stats as stats
from fvc.tools.flightlog.split import split_by_day, split_by_inactivity
import fvc.tools.df.utils as u


@click.group(
    name='flightlog',
    help='Flightlog tools'
)
def flightlog_group():
    pass


@flightlog_group.command(
    help='Calculate statistics for a FVC data file'
)
@click.pass_obj
@click.option(
    '--vdim',
    help='Vertical dimension metric to use for statistics', default='alt',
    type=click.Choice(['alt', 'height', 'amsl'])
)
@click.option(
    '--segment', type=float, help='Segment altitude'
)
def stats_command(params, **kwargs):
    params.update(kwargs)

    if params.get('vdim') == 'none':
        params['vdim'] = None

    with Live(Spinner('aesthetic', 'Analyzing...'), transient=True):
        stats.print_stats(params)


@flightlog_group.command(
    help='Split a flightlog into daily files'
)
@click.pass_obj
@click.option(
    '--mode',
    type=click.Choice(['day', 'inactivity']),
    help='Split mode', default='inactivity'
)
@click.option(
    '--inactivity-threshold-seconds',
    type=float,
    default=300.0,
    help='Inactivity threshold in seconds'
)
def split_command(params, **kwargs):
    params.update(kwargs)

    with Progress(transient=True) as progress:
        input_path = u.input_path(params)

        read_task = progress.add_task(
            'Reading...', total=input_path.stat().st_size
        )

        def callback(s):
            progress.update(read_task, advance=s)

        if params.get('mode') == 'inactivity':
            split_by_inactivity(params, callback=callback)
        else:
            split_by_day(params, callback=callback)
