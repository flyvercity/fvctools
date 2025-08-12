'''Manna's data dump format'''

from pathlib import Path
import csv
from datetime import datetime
import uuid
import logging as lg
from botobuddy.utils import dslice
from dateutil.parser import parse

from fvc.tools.df.utils import JsonlinesIO


def module_help():
    return '''\
- signal-select=<metric>: Select the signal metric to choose the best one. Options:
    - rsrp: Reference Signal Received Power (default)
    - rsrq: Reference Signal Received Quality
    - rssi: Received Signal Strength Indicator
'''


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    track_id = str(uuid.uuid4())

    signal_select = params.get('signal-select', 'rsrp')

    with input_path.open('rt') as input:
        reader = csv.DictReader(input, delimiter=',')

        metadata.update({
            'content': 'flightlog',
            'source': 'manna',
            'signal_select': signal_select
        })

        output.write(metadata)

        for row in reader:
            row_ts_str = row['utc_datetime']
            row_ts = parse(row_ts_str)
            timestamp = int(row_ts.timestamp() * 1000)
            uaid = {'int': track_id}

            maybe_float = lambda x: float(x) if x and x != '-' else None

            loc = dslice(
                row,
                {'k': 'lat', 'c': maybe_float},
                {'k': 'lon', 'c': maybe_float},
                {'k': 'alt_wgs84', 'c': maybe_float, 'n': 'alt'},
                {'k': 'alt_lidar', 'c': maybe_float, 'n': 'height'},
            )

            record = {
                'uaid': uaid,
                'time': {
                    'unix': timestamp,
                    'original': row_ts_str
                },
                'pos': {
                    'loc': loc
                }
            }

            output.write(record)


def old_convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    track_id = str(uuid.uuid4())

    allow_low_precision = 'gnettrack-allow-low-precision' in params.get('custom', [])

    with input_path.open('rt') as input:
        reader = csv.DictReader(input, delimiter='\t')

        metadata.update({
            'content': 'flightlog',
            'source': 'gnettrack',
            'allow_low_precision': allow_low_precision
        })

        output.write(metadata)

        for row in reader:
            row_ts = row['Timestamp']
            [date, time] = row_ts.split('_')
            [year, month, day] = date.split('.')
            time_parts = time.split('.')

            row_metadata = {}

            if len(time_parts) != 4:
                if allow_low_precision:
                    lg.warning('Using low precision time for Gnettrack log')
                    time_parts.append('0')
                    row_metadata['low_precision'] = True
                else:
                    raise UserWarning(
                        f'Invalid time setting for Gnettrack log {input_path.name}. '
                        'Please enable enhanced logging in the Calibrator config'
                    )

            [hour, minute, second, ms] = time_parts

            dt = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute), int(second),
                int(ms) * 1000
            )

            timestamp = int(dt.timestamp() * 1000)
            device = row['DEVICE']

            uaid = {'int': f'{device}:{track_id}'}
            uaid.update(dslice(row, 'IP', 'IMEI', 'IMSI'))

            maybe_float = lambda x: float(x) if x and x != '-' else None
            maybe_int = lambda x: int(x) if x and x != '-' else None

            net_tech = row['NetworkTech']
            net_mode = row['NetworkMode']

            match (net_tech, net_mode):
                case ('4G', 'LTE'):
                    radio = '4GLTE'
                case ('4G', '5G NSA') | ('5G', '5G NSA') | ('5G', 'LTE'):
                    radio = '5GNSA'
                case ('5G', 'NR'):
                    radio = '5GNR'
                case _:
                    lg.warning(f'Unknown network technology: {net_tech} {net_mode}')
                    continue

            cellsig = {'radio': radio}

            cellsig.update(dslice(
                row,
                {'k': 'Level', 'c': maybe_float, 'n': 'RSRP'},
                {'k': 'Qual', 'c': maybe_float, 'n': 'RSRQ'},
                {'k': 'LTERSSI', 'c': maybe_float, 'n': 'RSSI'},
                {'k': 'SNR', 'c': maybe_float, 'n': 'SINR'},
                {'k': 'CSI_PCI', 'c': maybe_float, 'n': 'CSI-RSRP'},
                {'k': 'CSI_RSRQ', 'c': maybe_float, 'n': 'CSI-RSRQ'},
                {'k': 'CSI_RSSI', 'c': maybe_float, 'n': 'CSI-RSSI'},
                {'k': 'CSI_SNR', 'c': maybe_float, 'n': 'CSI-SINR'},
                {'k': 'SS_Level', 'c': maybe_float, 'n': 'SS-RSRP'},
                {'k': 'SS_Qual', 'c': maybe_float, 'n': 'SS-RSRQ'},
                {'k': 'SS_RSSI', 'c': maybe_float, 'n': 'SS-RSSI'},
                {'k': 'SS_SNR', 'c': maybe_float, 'n': 'SS-SINR'},
                {'k': 'ARFCN', 'c': maybe_int},
                {'k': 'BAND', 'n': 'band'},
                {'k': 'Operator', 'n': 'plmnid'},
                {'k': 'Operatorname', 'n': 'plmnname'},
                {'k': 'CGI', 'n': 'CGI'}
            ))

            loc = dslice(
                row,
                {'k': 'Latitude', 'c': maybe_float, 'n': 'lat'},
                {'k': 'Longitude', 'c': maybe_float, 'n': 'lon'},
                {'k': 'Altitude', 'c': maybe_float, 'n': 'alt'}
            )

            datalink = dslice(
                row,
                {'k': 'PINGMAX', 'c': maybe_int, 'n': 'rtt'},
                {'k': 'PINGLOSS', 'c': maybe_int, 'n': 'loss'}
            )

            row_metadata.update(dslice(
                row,
                'BATTERY',
                'Accuracy',
                'Location',
            ))

            record = {
                'uaid': uaid,
                'time': {
                    'unix': timestamp,
                    'original': row_ts
                },
                'pos': {
                    'loc': loc
                },
                'cellsig': cellsig,
                'datalink': datalink,
                'metadata': row_metadata
            }

            output.write(record)
