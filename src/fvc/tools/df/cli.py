import importlib
from pathlib import Path

import click
from rich.progress import Progress

import fvc.tools.df.core as core
import fvc.tools.df.metadata as metadata
import fvc.tools.df.utils as dfu
from fvc.tools.df.correlate import correlate
from fvc.tools.df.fusion import fusion
from fvc.tools.utils import json_print
from fvc.tools.df.utils import lg

from fvc.tools.flightlog.cli import flightlog_group

DESCRIPTION = 'Data file conversion and manipulation tool'

EPILOG = """
Notes:
    For EGM geoid data download, visit:
    https://geographiclib.sourceforge.io/C++/doc/geoid.html#geoidinst

    To set a default cache directory, use the FVC_CACHE environment variable.
"""


@click.group(help=DESCRIPTION, epilog=EPILOG)
@click.pass_obj
@click.option(
    '--cache-dir',
    help='Directory for caching external data',
    type=Path,
    envvar='FVC_CACHE',
    required=False,
)
@click.option(
    '--in',
    'input_path',
    required=False,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    '--suffix',
    help='Suffix substitution for input files',
    type=str,
    required=False,
)
def df(params, **kwargs):
    params.update(kwargs)


@df.command(help='Validate a FVC file against the known schema')
@click.pass_obj
def validate(params):
    input_path = dfu.input_path(params)
    file_size = input_path.stat().st_size

    with Progress(transient=True) as progress:
        task = progress.add_task('Validating data', total=file_size)

        valid = core.validate(input_path, callback=lambda s: progress.update(task, advance=s))

        lg.info(f'Validation {"succeeded" if valid else "failed"}')

    if params['JSON']:
        json_print(params, {'valid': valid})


@df.command(name='help', help='Show help for a specific format')
@click.argument('x_format', type=str, required=True)
def xformat_help(x_format: str):
    ext_format_mod = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')

    help_text = getattr(ext_format_mod, 'module_help', None)

    if help_text:
        click.echo(f"Help for '{x_format}' additional parameters:")
        click.echo(help_text())
    else:
        lg.error(f'No help text found for {x_format}')


@df.command(name='convert')
@click.pass_obj
@click.option(
    '--target',
    help='Target content type',
    type=click.Choice(['flightlog', 'radarlog']),
    default='flightlog',
)
@click.option(
    '--custom',
    help='Custom parameters for the conversion, use "fvc.df help <x_format>" for details',
    type=str,
    multiple=True,
    required=False,
)
@click.argument('x_format', type=str, required=True)
@click.argument('output-file', type=Path, required=False)
@metadata.metadata_args
def convert_command(params, output_file, **kwargs):
    """Convert an external data file to the FVC format

    \b
    Available formats:
        - agentfly
        - artlog
        - courageous
        - datcon
        - gnettrack
        - nmea
        - robinradar
        - safirmqtt
        - senhive
        - ulog
    """

    params.update(kwargs)
    input_path = dfu.input_path(params)
    output_path = output_file if output_file else input_path.with_suffix('.fvc')

    if output_path.absolute() == input_path.absolute():
        lg.error('Input and output paths are the same')
        return

    params['input_path'] = input_path
    params['output_path'] = output_path

    with Progress(transient=True) as progress:
        read_task = progress.add_task('Converting...', total=input_path.stat().st_size)

        def callback(s):
            progress.update(read_task, advance=s)

        core.convert(params, callback)

    lg.info(f'Conversion complete, output written to {output_path}')


@df.command(
    name='export',
    help='Convert data to an external format'
)
@click.pass_obj
@click.argument('x_format', type=str, required=True)
@click.argument('output-file', type=Path, required=False)
def export_command(params, output_file, **kwargs):
    params.update(kwargs)
    params['output_path'] = output_file
    core.export(params)


@df.command(
    name='correlate',
    help='Correlate several flightlogs'
)
@click.pass_obj
@click.argument(
    'infiles',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    nargs=-1,
)
def correlate_command(params, infiles: tuple[Path, ...]):
    with Progress() as progress:
        check_tasks = [progress.add_task(f'Checking {infile}...', total=infile.stat().st_size) for infile in infiles]

        correlate(
            params,
            infiles,
            [lambda s: progress.update(check_tasks[i], advance=s) for i in range(len(check_tasks))],
        )


df.add_command(fusion)
df.add_command(flightlog_group)
