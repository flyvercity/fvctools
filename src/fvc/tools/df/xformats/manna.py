"""Manna's data dump format"""

import csv
import json
import uuid
from pathlib import Path

from botobuddy.utils import dslice

from fvc.tools.df.utils import JsonlinesIO, lg
from fvc.tools.utils import datestring_to_ts


def convert_to_fvc(
    params,
    metadata,
    input_path: Path,
    output: JsonlinesIO,
):
    track_id = str(uuid.uuid4())

    with input_path.open('rt') as input:
        reader = csv.DictReader(input, delimiter=',')

        modems = list(filter(lambda x: str(x).startswith('modem'), reader.fieldnames or []))
        lg.debug(f'Modems found: {modems}')

        metadata.update(
            {
                'content': 'flightlog',
                'source': 'manna',
                'cellsig': {'modems': modems},
            }
        )

        output.write(metadata)

        def maybe_float(x):
            if x and x not in ('-', 'NULL'):
                return float(x)

            return None

        rows_read = 0
        signals_found = 0

        for row in reader:
            rows_read += 1
            row_ts_str = row['utc_datetime']

            # ⚡ Bolt: Use datestring_to_ts for fast path ISO-8601 parsing.
            # datetime.fromisoformat is ~40x faster than dateutil.parser.parse
            timestamp = datestring_to_ts(row_ts_str)
            uaid = {'int': track_id}

            loc = dslice(
                row,
                {'k': 'lat', 'c': maybe_float},
                {'k': 'lon', 'c': maybe_float},
                {'k': 'alt_wgs_84', 'c': maybe_float, 'n': 'alt'},
                {'k': 'alt_lidar', 'c': maybe_float, 'n': 'height'},
            )

            record = {
                'uaid': uaid,
                'time': {'unix': timestamp, 'original': row_ts_str},
                'pos': {'loc': loc},
            }

            modem_data_dict = {}

            for modem_name in modems:
                modem_data = _get_modem_data(row, modem_name, reader.line_num)

                if modem_data:
                    modem_data_dict[modem_name] = modem_data

            if modem_data_dict:
                record['cellsig'] = {'multi': modem_data_dict}
                signals_found += 1

            output.write(record)

        lg.info(f'Rows read: {rows_read}, signals found: {signals_found}')


def _get_modem_data(row, modem_name, line_number):
    try:
        modem_data_str = row[modem_name]
        lg.debug(f'Modem data: {modem_data_str}')
        modem_data = json.loads(modem_data_str)

        cellsig = dslice(
            modem_data,
            {'k': 'rsrp', 'n': 'rsrp'},
            {'k': 'rsrq', 'n': 'rsrq'},
            {'k': 'rssi', 'n': 'rssi'},
            {'k': 'operator_name', 'n': 'plmnname'},
        )

        plmnid = modem_data.get('operator_num')
        cell_lac = modem_data.get('cell_lac')
        cell_tac = modem_data.get('cell_tac')

        if cell_lac != 0:
            ac = cell_lac
            radio = '2G3G'
        elif cell_tac != 0:
            ac = cell_tac
            radio = '4GLTE'
        else:
            lg.debug(f'Unknown network technology: {plmnid} {cell_lac} {cell_tac}')
            radio = 'Unknown'

        cell_id = modem_data.get('cell_id')
        cgi = f'{plmnid}{ac:05d}{cell_id:05d}'

        cellsig.update({'radio': radio, 'plmnid': plmnid, 'cgi': cgi})

        return cellsig

    except Exception as e:
        lg.debug(f'Error getting modem data for {modem_name} at line {line_number}: {e}')
        return None
