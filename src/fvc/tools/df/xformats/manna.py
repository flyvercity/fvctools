"""Manna's data dump format"""

import copy
import csv
import json
import uuid
from pathlib import Path

from botobuddy.utils import dslice
from dateutil.parser import parse

from fvc.tools.df.utils import JsonlinesIO, lg


def module_help():
    return """\
- signal-select=<metric>: Select the signal metric to choose the best one. Options:
    - rsrp: Reference Signal Received Power (default)
    - rsrq: Reference Signal Received Quality
    - rssi: Received Signal Strength Indicator
"""


def convert_to_fvc(
    params, metadata, input_path: Path, output: JsonlinesIO
):
    track_id = str(uuid.uuid4())

    signal_select = 'rsrp'

    for custom in params.get('custom', []):
        if custom.startswith('signal-select='):
            signal_select = custom.split('=')[1]
            break

    if signal_select not in ('rsrp', 'rsrq', 'rssi'):
        raise UserWarning(
            f'Invalid signal select: {signal_select}. Valid options are: rsrp, rsrq, rssi'
        )

    with input_path.open('rt') as input:
        reader = csv.DictReader(input, delimiter=',')

        modems = list(
            filter(
                lambda x: str(x).startswith('modem'), reader.fieldnames or []
            )
        )
        lg.debug(f'Modems found: {modems}')

        metadata.update(
            {
                'content': 'flightlog',
                'source': 'manna',
                'signal_select': signal_select,
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
            row_ts = parse(row_ts_str)
            timestamp = int(row_ts.timestamp() * 1000)
            uaid = {'int': track_id}

            loc = dslice(
                row,
                {'k': 'lat', 'c': maybe_float},
                {'k': 'lon', 'c': maybe_float},
                {'k': 'alt_wgs84', 'c': maybe_float, 'n': 'alt'},
                {'k': 'alt_lidar', 'c': maybe_float, 'n': 'height'},
            )

            record = {
                'uaid': uaid,
                'time': {'unix': timestamp, 'original': row_ts_str},
                'pos': {'loc': loc},
            }

            best_cellsig = None
            best_signal = None
            modem_data_dict = {}

            for modem_name in modems:
                modem_data = _get_modem_data(row, modem_name, reader.line_num)

                if modem_data:
                    modem_data_dict[modem_name] = modem_data
                    signal = modem_data.get(signal_select)

                    if signal is not None and (
                        best_signal is None or signal > best_signal
                    ):
                        best_signal = signal
                        best_cellsig = copy.deepcopy(modem_data)

            if best_cellsig:
                record['cellsig'] = best_cellsig
                record['cellsig']['modems'] = modem_data_dict
                signals_found += 1

            output.write(record)

        lg.info(f'Rows read: {rows_read}, signals found: {signals_found}')


def _get_modem_data(row, modem_name, line_number):
    try:
        modem_data_str = row[modem_name]
        lg.debug(f'Modem data: {modem_data_str}')
        modem_data = json.loads(modem_data_str)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        lg.warning(
            f'Error parsing modem data for {modem_name} at line {line_number}: {e}'
        )
        return None

    try:
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
            lg.debug(
                f'Unknown network technology: {plmnid} {cell_lac} {cell_tac}'
            )
            radio = 'Unknown'

        cell_id = modem_data.get('cell_id')
        cgi = f'{plmnid}{ac:05d}{cell_id:05d}'
        cellsig.update({'radio': radio, 'plmnid': plmnid, 'CGI': cgi})
        return cellsig

    except Exception as e:
        lg.exception(
            f'Error getting modem data for {modem_name} at line {line_number}: {e}'
        )
        return None
