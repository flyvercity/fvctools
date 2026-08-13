import click
import json
from pathlib import Path

import rich
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress
import polars as pl

import fvc.tools.utils as u
import fvc.tools.df.utils as dfu
import fvc.tools.flightlog.segment as segment
import fvc.tools.flightlog.stats as stats
from fvc.tools.flightlog.split import split_by_day, split_by_inactivity
import fvc.tools.flightlog.load as load


@click.group(name='flightlog', help='Flightlog tools')
def flightlog_group():
    pass


@flightlog_group.command(help='Calculate statistics for a FVC data file')
@click.pass_obj
@click.option(
    '--vdim',
    help='Vertical dimension metric to use for statistics',
    default='alt',
    type=click.Choice(['alt', 'height', 'amsl']),
)
@click.option('--segment-by-height', is_flag=True, help='Segment the log by height')
@click.option(
    '--segment-height-meters',
    type=float,
    help='Height to segment the log by in meters',
    default=10.0,
)
@click.option('--segment-by-idle', is_flag=True, help='Segment the log by idle time')
@click.option(
    '--idle-time-seconds',
    type=float,
    help='Idle time to segment the log by in seconds',
    default=60.0,
)
@click.option('--filter-by-duration', is_flag=True, help='Filter the log by duration')
@click.option('--filter-duration-seconds', type=float, help='Duration to filter the log by in seconds', default=300.0)
@click.option('--filter-displacement/--no-filter-displacement', default=False,
              help='Filter segments by spatial displacement')
@click.option('--displacement-lateral-meters', type=float, default=200.0,
              help='Minimum lateral diagonal displacement in meters')
@click.option('--displacement-vertical-meters', type=float, default=50.0,
              help='Minimum vertical displacement in meters')
@click.option('--verbose', is_flag=True, help='Verbose output')
def stats_command(params, **kwargs):
    params.update(kwargs)

    with Live(Spinner('aesthetic', 'Analyzing...'), transient=True):
        input_path = dfu.input_path(params)
        dataset = load.load_frames(input_path)

        seg_params = segment.SegmentParams(
            segment_by_height=params.get('segment_by_height', False),
            segment_height_meters=params.get('segment_height_meters', 10.0),
            airborne_only=True,
            segment_by_idle=params.get('segment_by_idle', False),
            idle_time_seconds=params.get('idle_time_seconds', 60.0),
            filter_by_duration=params.get('filter_by_duration', False),
            filter_duration_seconds=params.get('filter_duration_seconds', 300.0),
            filter_by_displacement=params.get('filter_displacement', False),
            filter_displacement_lateral_meters=params.get('displacement_lateral_meters', 200.0),
            filter_displacement_vertical_meters=params.get('displacement_vertical_meters', 50.0),
        )

        result_dataset, metadata = segment.segment(dataset, seg_params)

        dfu.lg.info(f'Processing metadata:\n{json.dumps(metadata, indent=4)}')

        stats.print_stats(result_dataset, vdim=params.get('vdim'))


@flightlog_group.command(help='Split a flightlog into daily files')
@click.pass_obj
@click.option('--mode', type=click.Choice(['day', 'inactivity']), help='Split mode', default='inactivity')
@click.option('--inactivity-threshold-seconds', type=float, default=300.0, help='Inactivity threshold in seconds')
@click.option(
    '--output-dir',
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=Path,
    ),
    help='Output directory',
    required=False,
)
def split_command(params, **kwargs):
    params.update(kwargs)

    with Progress(transient=True) as progress:
        input_path = dfu.input_path(params)

        read_task = progress.add_task('Reading...', total=input_path.stat().st_size)

        def callback(s):
            progress.update(read_task, advance=s)

        if params.get('output_dir') is None:
            params['output_dir'] = input_path.parent / 'split'

        if params.get('mode') == 'inactivity':
            split_by_inactivity(params, callback=callback)
        else:
            split_by_day(params, callback=callback)


@flightlog_group.command(name='select', help='Fetch a given element from the flight log')
@click.pass_obj
@click.option('--format', type=click.Choice(['fvc', 'frames', 'ndjson']), default='frames')
@click.argument('expression')
def select_command(obj, format, expression):
    input_path = dfu.input_path(obj)

    if input_path.suffix == '.fvc' and format != 'fvc':
        dfu.lg.warning(
            'You are selecting from a FVC file, but the format is not frames. This will likely result in an error.'
        )

    match format:
        case 'fvc':
            dataset = load.load_frames(input_path)
            frames = dataset.frames
        case 'frames':
            dataset = load.FlightlogDataset.deserialize(input_path)
            frames = dataset.frames
        case 'ndjson':
            df = [pl.read_ndjson(input_path)]

    if not obj['JSON']:
        for inx, frame in enumerate(frames):
            rich.print(f'----- Frame {inx} ----')
            df = frame.select(u.plnested(expression))
            rich.print(df)
    else:
        json_frames = [frame.to_dicts() for frame in frames]
        click.echo(json.dumps(json_frames, indent=4))
