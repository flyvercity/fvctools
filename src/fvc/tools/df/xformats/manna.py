"""Manna's data dump format"""

import copy
import csv
import json
import logging as lg
import uuid
from datetime import datetime
from pathlib import Path

from botobuddy.utils import dslice
from dateutil.parser import parse

from fvc.tools.df.utils import JsonlinesIO


def module_help():
    return """\
- signal-select=<metric>: Select the signal metric to choose the best one. Options:
    - RSRP: Reference Signal Received Power (default)
    - RSRQ: Reference Signal Received Quality
    - RSSI: Received Signal Strength Indicator
"""


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    track_id = str(uuid.uuid4())

    signal_select = params.get('signal-select', 'RSRP')

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

        # Optimization: Try to guess the date format from common formats
        # and reuse it for subsequent rows using datetime.strptime
        date_format = None
        common_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%f',
        ]

        for row in reader:
            row_ts_str = row['utc_datetime']

            row_ts = None
            if date_format:
                try:
                    row_ts = datetime.strptime(row_ts_str, date_format)
                except ValueError:
                    # Fallback if the cached format fails
                    date_format = None

            if row_ts is None:
                # Try to find a matching format
                for fmt in common_formats:
                    try:
                        row_ts = datetime.strptime(row_ts_str, fmt)
                        date_format = fmt
                        break
                    except ValueError:
                        continue

                # Ultimate fallback
                if row_ts is None:
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

            output.write(record)


def _get_modem_data(row, modem_name, line_number):
    try:
        modem_data_str = row[modem_name]
        modem_data = json.loads(modem_data_str)

        cellsig = dslice(
            modem_data,
            {'k': 'rsrp', 'n': 'RSRP'},
            {'k': 'rsrq', 'n': 'RSRQ'},
            {'k': 'rssi', 'n': 'RSSI'},
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
            lg.warning(
                f'Unknown network technology: {plmnid} {cell_lac} {cell_tac}'
            )
            return None

        cell_id = modem_data.get('cell_id')
        cgi = f'{plmnid}{ac:05d}{cell_id:05d}'

        cellsig.update({'radio': radio, 'plmnid': plmnid, 'CGI': cgi})

        return cellsig

    except Exception as e:
        lg.debug(
            f'Error getting modem data for {modem_name} at line {line_number}: {e}'
        )
        return None
