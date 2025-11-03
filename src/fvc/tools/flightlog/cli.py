import click
from rich.live import Live
from rich.spinner import Spinner
import fvc.tools.flightlog.stats as stats


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
    '--vdim', type=str, help='Dimension to visualize', default='alt'
)
@click.option('--segment', type=float, help='Segment altitude')
def stats_command(params, **kwargs):
    params.update(kwargs)

    if params.get('vdim') == 'none':
        params['vdim'] = None

    with Live(
        Spinner('aesthetic', 'Analyzing...'),
        transient=True,
    ):
        stats.print_stats(params)
