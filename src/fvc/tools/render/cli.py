import logging as lg
import webbrowser
from pathlib import Path

import click

from fvc.tools.render.core import generate_html_map


@click.group(help='Render FVC data files')
def render():
    pass


@render.command(name='fl', help='Generate map visualization for FVC data files')
@click.pass_obj
@click.argument('filename', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    default=Path('./results/render'),
    help='Output directory for generated files (default: ./results/render)',
)
@click.option(
    '--title',
    default='FVC Data Visualization',
    help='Title for the visualization',
)
def render_flightlog(obj, filename, output, title):
    """Generate an interactive map visualization for FVC data files.

    This command reads FVC format files (jsonlines) and creates an HTML
    visualization showing the flight path on an interactive map.
    """

    lg.info(f'Generating visualization for {filename}')
    lg.info(f'Output directory: {output}')
    output.mkdir(parents=True, exist_ok=True)

    try:
        generate_html_map(filename, output, title)
        lg.info(f'Visualization generated successfully in {output}')
        try:
            lg.info(
                f'Opening {output / "index.html"} in your browser to view the map'
            )
            webbrowser.open(str(output / 'index.html'))

        except Exception:
            lg.info(
                f'Open {output / "index.html"} in your browser to view the map'
            )

    except Exception as e:
        lg.error(f'Failed to generate visualization: {e}')
        raise click.ClickException(str(e))
