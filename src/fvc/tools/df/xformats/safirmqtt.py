import traceback
from pathlib import Path

import fvc.tools.utils as u
from fvc.tools.df.utils import JsonlinesIO, lg


def from_safir_ids(safir_ids):
    ids = {}

    for safir_id in safir_ids:
        if safir_id.get('version') != '1':
            raise UserWarning(
                f'Unsupported version {safir_id.get("version")} in SAFIR ID'
            )

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

    if version != '1':
        raise UserWarning(
            f'Unsupported version {version} in SAFIR location record'
        )

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
        lg.warning(
            f'No AMSL found in safir location record (geodetic is {present})'
        )

    return record


def flightlog_record(record, geoid):
    if record.get('version') != '1':
        raise UserWarning(
            f'Unsupported version {record.get("version")} in SAFIR record'
        )

    if 'timestamp' not in record:
        raise UserWarning('No timestamp found in SAFIR record')

    time = u.datestring_to_ts(record.get('timestamp', ''))
    rec_ids = record.get('identifiers')

    if rec_ids is None:
        raise UserWarning('No identifiers found in SAFIR record')

    ids = from_safir_ids(rec_ids)
    rec_loc = record.get('location')
    pos = from_safir_loc(rec_loc, geoid)
    origin = record.get('origin')

    record = {'time': {'unix': time}, 'uaid': ids, 'pos': pos, 'origin': origin}

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

        except UserWarning as e:
            if params['verbose']:
                traceback.print_exc()

            lg.warning(
                f'Error processing {input_path}:{input.in_line_no()}: {e}'
            )
