import click
import json
from pathlib import Path

from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress

import fvc.tools.flightlog.segment as segment
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
    '--segment-by-height', is_flag=True,
    help='Segment the log by height'
)
@click.option(
    '--segment-height-meters', type=float,
    help='Height to segment the log by in meters',
    default=10.0,
)
@click.option(
    '--segment-by-idle', is_flag=True,
    help='Segment the log by idle time'
)
@click.option(
    '--idle-time-seconds', type=float,
    help='Idle time to segment the log by in seconds',
    default=60.0,
)
@click.option(
    '--filter-by-duration', is_flag=True,
    help='Filter the log by duration'
)
@click.option(
    '--filter-duration-seconds', type=float,
    help='Duration to filter the log by in seconds',
    default=300.0
)
@click.option(
    '--verbose', is_flag=True,
    help='Verbose output'
)
def stats_command(params, **kwargs):
    params.update(kwargs)

    with Live(Spinner('aesthetic', 'Analyzing...'), transient=True):
        frames, metadata = segment.segment(params)

        u.lg.info(
            f'Processing metadata:\n{json.dumps(metadata, indent=4)}'
        )

        stats.print_stats(frames, vdim=params.get('vdim'))


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
@click.option(
    '--output-dir',
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True,
        path_type=Path,
    ),
    help='Output directory',
    required=False,
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

        if params.get('output_dir') is None:
            params['output_dir'] = input_path.parent / 'split'

        if params.get('mode') == 'inactivity':
            split_by_inactivity(params, callback=callback)
        else:
            split_by_day(params, callback=callback)
