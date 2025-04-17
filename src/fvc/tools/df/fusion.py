from pathlib import Path
import logging as lg

import click

import fvc.tools.df.util as u
from fvc.tools.df.util import JsonlinesIO as JLIO
import fvc.tools.df.xformats.safirmqtt as smq


def extract_flightlogs(params, replay: JLIO, plots: JLIO, tracks: JLIO):
    metadata = replay.read()

    if not metadata:
        raise UserWarning('No metadata found')

    if (content := metadata.get('content')) != 'fusion.replay':
        raise UserWarning(f'Unsupported content type: {content}')

    out_metadata = {
        'origin': str(params['input']),
        'content': 'flightlog',
        'source': 'fusion.replay'
    }

    geoid = u.load_geoid(params, out_metadata)
    plots.write(out_metadata)
    tracks.write(out_metadata)

    for record in replay.iterate():
        event = record.get('event')

        if event not in ['input', 'output']:
            continue

        fligtlog_rec = smq.flightlog_record(record['message'], geoid)

        if record['event'] == 'input':
            plots.write(fligtlog_rec)

        if record['event'] == 'output':
            fligtlog_rec['fusion'] = True
            tracks.write(fligtlog_rec)


@click.command(help='Extract fused flight log data from a replay file')
@click.option('--output-plots', type=Path, help='Output file for plots')
@click.option('--output-tracks', type=Path, help='Output file for tracks')
@click.pass_obj
def flightlog(params, output_plots, output_tracks):
    with u.JsonlinesIO(params['input'].fetch(), 'r') as replay:
        with u.JsonlinesIO(output_plots, 'w') as plots:
            with u.JsonlinesIO(output_tracks, 'w') as tracks:
                extract_flightlogs(params, replay, plots, tracks)
    
    lg.info(f'Flight log data extracted from {params["input"]}')


@click.group(help='A tool for SAFIR Fusion data files')
def fusion():
    pass


fusion.add_command(flightlog)
