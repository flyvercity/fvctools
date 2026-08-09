"""
Gnettrack log format
"""

import csv
import uuid
from datetime import datetime
from pathlib import Path

from botobuddy.utils import dslice

from fvc.tools.df.utils import JsonlinesIO, lg


def module_help():
    """Module custom parameters"""
    return '- gnettrack-allow-low-precision: Allow low precision time for Gnettrack log'


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    track_id = str(uuid.uuid4())

    allow_low_precision = 'gnettrack-allow-low-precision' in params.get('custom', [])

    if allow_low_precision:
        lg.debug('Allowing low precision time for Gnettrack log')
    else:
        lg.debug('Not allowing low precision time for Gnettrack log')

    with input_path.open('rt') as input:
        reader = csv.DictReader(input, delimiter='\t')

        metadata.update(
            {
                'content': 'flightlog',
                'source': 'gnettrack',
                'allow_low_precision': allow_low_precision,
            }
        )

        output.write(metadata)

        for row in reader:
            row_ts = row['Timestamp']
            row_metadata = {}

            # ⚡ Bolt: Fast-path ISO-8601 parsing (~5x speedup over split + datetime instantiation).
            # We convert row_ts (e.g. '2023.10.11_12.30.45.123') to ISO format ('2023-10-11T12:30:45.123')
            # and parse it with datetime.fromisoformat.
            # But Gnettrack files can also contain low-precision timestamps (e.g., '2023.10.11_12.30.45' which doesn't have millisecond component).
            # If so, we need to detect it. A standard format has time parts separated by dots: '12.30.45.123'.
            # Let's count how many dots are in the time component (after the '_').
            if '_' in row_ts:
                time_part = row_ts.split('_')[1]
                time_parts_count = len(time_part.split('.'))
            else:
                time_parts_count = 0

            if time_parts_count != 4:
                if allow_low_precision:
                    lg.warning('Using low precision time for Gnettrack log')
                    row_metadata['low_precision'] = True
                else:
                    raise UserWarning(
                        f'Invalid time setting for Gnettrack log {input_path.name}. '
                        'Please enable enhanced logging in the Calibrator config'
                    )

            try:
                # Replace the first two dots with hyphens (date separator), underscore with T,
                # and up to next two dots with colons (time separator), keeping millisecond dot intact.
                dt_iso = row_ts.replace('.', '-', 2).replace('_', 'T').replace('.', ':', 2)
                dt = datetime.fromisoformat(dt_iso)
            except ValueError:
                raise UserWarning(
                    f'Invalid time setting for Gnettrack log {input_path.name}. '
                    'Please enable enhanced logging in the Calibrator config'
                )

            timestamp = int(dt.timestamp() * 1000)
            device = row.get('DEVICE', 'unknown-device')

            uaid = {'int': f'{device}:{track_id}'}
            uaid.update(dslice(row, {'k': 'IP', 'n': 'ip'}, {'k': 'IMEI', 'n': 'imei'}, {'k': 'IMSI', 'n': 'imsi'}))

            def maybe_float(x):
                return float(x) if x and x != '-' else None

            def maybe_int(x):
                return int(x) if x and x != '-' else None

            net_tech = row['NetworkTech']
            net_mode = row['NetworkMode']

            match (net_tech, net_mode):
                case ('2G', 'EDGE') | ('2G', 'LTE') | ('2G', 'GPRS'):
                    radio = '2G`'
                case ('4G', 'LTE'):
                    radio = '4GLTE'
                case ('4G', '5G NSA') | ('5G', '5G NSA') | ('5G', 'LTE'):
                    radio = '5GNSA'
                case ('5G', 'NR'):
                    radio = '5GNR'
                case _:
                    lg.warning(f'Unknown network technology: {net_tech} {net_mode}')
                    radio = 'Unknown'
                    continue

            cellsig = {'radio': radio}

            cellsig.update(
                dslice(
                    row,
                    {'k': 'Level', 'c': maybe_float, 'n': 'rsrp'},
                    {'k': 'Qual', 'c': maybe_float, 'n': 'rsrq'},
                    {'k': 'LTERSSI', 'c': maybe_float, 'n': 'rssi'},
                    {'k': 'SNR', 'c': maybe_float, 'n': 'sinr'},
                    {'k': 'CSI_PCI', 'c': maybe_float, 'n': 'csi-rsrp'},
                    {'k': 'CSI_RSRQ', 'c': maybe_float, 'n': 'csi-rsrq'},
                    {'k': 'CSI_RSSI', 'c': maybe_float, 'n': 'csi-rssi'},
                    {'k': 'CSI_SNR', 'c': maybe_float, 'n': 'csi-sinr'},
                    {'k': 'SS_Level', 'c': maybe_float, 'n': 'ss-rsrp'},
                    {'k': 'SS_Qual', 'c': maybe_float, 'n': 'ss-rsrq'},
                    {'k': 'SS_RSSI', 'c': maybe_float, 'n': 'ss-rssi'},
                    {'k': 'SS_SNR', 'c': maybe_float, 'n': 'ss-sinr'},
                    {'k': 'ARFCN', 'c': maybe_int},
                    {'k': 'BAND', 'n': 'band'},
                    {'k': 'Operator', 'n': 'plmnid'},
                    {'k': 'Operatorname', 'n': 'plmnname'},
                    {'k': 'CGI', 'n': 'cgi'},
                )
            )

            loc = dslice(
                row,
                {'k': 'Latitude', 'c': maybe_float, 'n': 'lat'},
                {'k': 'Longitude', 'c': maybe_float, 'n': 'lon'},
                {'k': 'Altitude', 'c': maybe_float, 'n': 'alt'},
            )

            def nonzero(x):
                if not x:
                    return None

                return int(x) != 0

            datalink = dslice(
                row,
                {'k': 'PINGMAX', 'c': maybe_int, 'n': 'rtt'},
                {'k': 'PINGLOSS', 'c': nonzero, 'n': 'loss'},
            )

            row_metadata.update(
                dslice(
                    row,
                    'BATTERY',
                    'Accuracy',
                    'Location',
                )
            )

            record = {
                'uaid': uaid,
                'time': {'unix': timestamp, 'original': row_ts},
                'pos': {'loc': loc},
                'cellsig': cellsig,
                'datalink': datalink,
                'metadata': row_metadata,
            }

            output.write(record)
