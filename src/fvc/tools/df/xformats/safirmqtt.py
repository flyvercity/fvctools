from pathlib import Path
import logging as lg
import traceback

from dateutil.parser import parse as dateparse

import fvc.tools.util as u
from fvc.tools.df.util import JsonlinesIO

def from_safir_ids(safir_ids):
    ids = {}

    for safir_id in safir_ids:
        assert safir_id.get('version') == '1'
        system = safir_id.get('system')
        key = safir_id.get('key')

        if system == 'ICAOHex':
            ids['icaohex'] = key
        elif system == 'ICAORegistration':
            ids['icaoreg'] = key
        elif system == 'CallSign':
            ids['atm'] = key
        if system == 'Other':
            ids['int'] = key

        if 'int' not in ids:
            # If no internal ID is present, use the first one found
            ids['int'] = key

    return ids


def from_safir_loc(safir_loc, geoid):
    version = safir_loc.get('version')
    lat = safir_loc.get('latitude')
    lon = safir_loc.get('longitude')
    amsl = safir_loc.get('altitudeAMSL')

    assert version == '1'
    assert lat is not None
    assert lon is not None
    assert amsl is not None

    alt = u.amsl_to_ellipsoidal(geoid, lat, lon, amsl)

    return {
        'loc': {
            'lat': lat,
            'lon': lon,
            'alt': alt
        }
    }


def flightlog_record(record, geoid):
    assert record.get('version') == '1'
    assert 'timestamp' in record
    time = u.datestring_to_ts(record.get('timestamp', ''))
    rec_ids = record.get('identifiers')
    assert rec_ids
    ids = from_safir_ids(rec_ids)
    rec_loc = record.get('location')
    pos = from_safir_loc(rec_loc, geoid)
    origin = record.get('origin')

    record = {
        'time': {'unix': time},
        'uaid': ids,
        'pos': pos,
        'origin': origin
    }

    return record


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    geoid = u.load_geoid(params, metadata)
    metadata.update({'content': 'flightlog', 'source': 'safirmqtt'})
    output.write(metadata)

    with JsonlinesIO(input_path, 'r') as input:
        try:
            for record in input.iterate():
                fl_record = flightlog_record(record, geoid)
                output.write(fl_record)

        except Exception as e:
            if params['verbose']:
                traceback.print_exc()

            lg.warning(f'Error processing {input_path}:{input.in_line_no()}: {e}')
