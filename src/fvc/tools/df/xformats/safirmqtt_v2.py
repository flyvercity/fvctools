import traceback
from pathlib import Path

import fvc.tools.utils as u
from fvc.tools.df.utils import JsonlinesIO, lg


def from_safir_ids(safir_ids):
    ids = {}

    for safir_id in safir_ids:
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
    lat = safir_loc.get('latitude')
    lon = safir_loc.get('longitude')
    amsl = safir_loc.get('altitudeAMSL')

    if lat is None:
        raise UserWarning('No latitude found in SAFIR location record')

    if lon is None:
        raise UserWarning('No longitude found in SAFIR location record')

    record = {'loc': {'lat': lat, 'lon': lon}}

    if amsl is not None:
        alt = u.amsl_to_ellipsoidal(geoid, lat, lon, amsl)
        record['loc']['alt'] = alt

    else:
        present = 'present' if 'altitudeAMSL' in safir_loc else 'also missing'

        # TODO: Collect error statistics
        lg.debug(
            f'No AMSL found in SAFIR location record (geodetic is {present})'
        )

    return record


def flightlog_record(record, geoid):
    payload = record.get('payload')

    if payload is None:
        raise UserWarning('No payload found in MQTT record')

    if 'timestamp' not in payload:
        raise UserWarning('No timestamp found in SAFIR record')

    time = u.datestring_to_ts(payload.get('timestamp', ''))

    rec_ids = payload.get('identifiers')

    if rec_ids is None:
        raise UserWarning('No identifiers found in MQTT record')

    ids = from_safir_ids(rec_ids)
    rec_loc = payload.get('location')
    pos = from_safir_loc(rec_loc, geoid)
    origin = payload.get('origin')

    fvc_record = {
        'time': {'unix': time},
        'uaid': ids,
        'pos': pos,
        'origin': origin,
    }

    return fvc_record


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    geoid = u.load_geoid(params, metadata)
    metadata.update({'content': 'flightlog', 'source': 'safirmqtt'})
    output.write(metadata)

    with JsonlinesIO(input_path, 'r') as input:
        try:
            metadata = input.read()

            if metadata.get('content') != 'capture.message':
                raise UserWarning('Incoming content is not "capture.message"')

            for record in input.iterate():
                fl_record = flightlog_record(record, geoid)
                output.write(fl_record)

        except UserWarning as e:
            if params['verbose']:
                traceback.print_exc()

            lg.warning(
                f'Error processing {input_path}:{input.in_line_no()}: {e}'
            )
