import importlib
from pathlib import Path
import logging as lg

from rich.progress import Progress
import click

from fvc.tools.utils import json_print
import fvc.tools.df.utils as u
import fvc.tools.df.metadata as metadata
import fvc.tools.df.flightlog as flightlog
import fvc.tools.df.core as core
from fvc.tools.df.correlate import correlate
from fvc.tools.df.fusion import fusion


DESCRIPTION = 'Data file conversion and manipulation tool'

EPILOG = '''
Notes:

    For EGM geoid data download, visit:
    https://geographiclib.sourceforge.io/C++/doc/geoid.html#geoidinst

    To set a default cache directory, use the FVC_CACHE environment variable.

    From examples of 'fvc.df.toml' files, see 'examples/df' directory in the source code.
'''


@click.group(help=DESCRIPTION, epilog=EPILOG)
@click.pass_obj
@click.option(
    '--cache-dir', help='Directory for caching external data',
    type=Path, envvar='FVC_CACHE', required=False
)
@click.option(
    '--in', 'input', required=False
)
@click.option(
    '--suffix', help='Suffix substitution for input files',
    type=str, required=False
)
def df(params, input, **kwargs):
    params.update(kwargs)
    params['input'] = u.Input(params, input)


@df.command(help='Validate a FVC file against the known schema')
@click.pass_obj
def validate(params):
    input_path = params['input'].fetch()
    file_size = input_path.stat().st_size

    with Progress(transient=True) as progress:
        task = progress.add_task('Validating data', total=file_size)

        valid = core.validate(
            input_path,
            callback=lambda s: progress.update(task, advance=s)
        )

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


@df.command()
@click.pass_obj
@click.option(
    '--target', help='Target content type',
    type=click.Choice(['flightlog', 'radarlog']), default='flightlog'
)
@click.option(
    '--custom',
    help='Custom parameters for the conversion, use "fvc.df help <x_format>" for details',
    type=str,
    multiple=True,
    required=False
)
@click.argument('x_format', type=str, required=True)
@click.argument('output-file', type=Path, required=False)
@metadata.metadata_args
def convert_command(params, output_file, **kwargs):
    '''Convert an external data file to the FVC format

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
    '''

    params.update(kwargs)
    input_path = params['input'].fetch()
    output_path = output_file if output_file else input_path.with_suffix('.fvc')

    if output_path.absolute() == input_path.absolute():
        lg.error('Input and output paths are the same')
        return

    params['output_path'] = output_path

    with Progress(transient=True) as progress:
        read_task = progress.add_task('Converting...', total=input_path.stat().st_size)

        def callback(s):
            progress.update(read_task, advance=s)

        core.convert(params, input_path, callback)

    lg.info(f'Conversion complete, output written to {output_path}')


@df.command(help='Calculate statistics for a FVC data file')
@click.pass_obj
def stats(params):
    input_path = params['input'].fetch()

    with u.JsonlinesIO(input_path, 'r') as io:
        flightlog.stats(params, io)


@df.command(help='Just download and cache external data')
@click.pass_obj
def fetch(params):
    params['input'].fetch()

    if not params['JSON']:
        lg.info('This file is available in the cache')
    else:
        path = str(params['input'].fetch().resolve())
        json_print(params, {'path': path})


@df.command(help='Convert data to an external format')
@click.pass_obj
@click.argument('x_format', type=str, required=True)
@click.argument('output-file', type=Path, required=False)
def export_command(params, output_file, **kwargs):
    params.update(kwargs)
    params['output_path'] = output_file
    core.export(params)


@df.command(help='Scan for fvc.df.toml files and execute tasks')
@click.pass_obj
@click.option('--force', help='Reconvert files even if they exist', is_flag=True)
@click.option('--validate', help='Validate files after conversion', is_flag=True)
def crawl(params, force, validate):
    params['force'] = force
    params['validate'] = validate
    core.crawl(params)


@df.command(help='Upgrade a FVC file to the latest schema (volatile code)')
@click.argument('infile', type=click.Path(exists=True, path_type=Path), required=True)
@click.pass_obj
def upgrade(params, infile):
    params['input'] = u.Input(params, infile)
    params['output_path'] = infile.with_suffix('.fvc')

    with Progress(transient=True) as progress:
        read_task = progress.add_task('Reading...', total=infile.stat().st_size)
        write_task = progress.add_task('Writing...', total=infile.stat().st_size)

        core.upgrade(
            params,
            lambda s: progress.update(read_task, advance=s),
            lambda s: progress.update(write_task, advance=s)
        )


@df.command(help='Correlate several flightlogs')
@click.pass_obj
@click.argument(
    'infiles',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    nargs=-1
)
def correlate_command(params, infiles: tuple[Path, ...]):
    with Progress() as progress:
        check_tasks = [
            progress.add_task(f'Checking {infile}...', total=infile.stat().st_size)
            for infile in infiles
        ]

        merge_task = progress.add_task('Merging...', total=None)

        correlate(
            params, infiles,
            [
                lambda s: progress.update(check_tasks[i], advance=s)
                for i in range(len(check_tasks))
            ],
            lambda s: progress.update(merge_task, advance=s)
        )


df.add_command(fusion)
