from pathlib import Path
import csv
from datetime import datetime
import uuid
import logging as lg
from botobuddy.utils import dslice

from fvc.tools.df.util import JsonlinesIO


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    track_id = str(uuid.uuid4())

    with input_path.open('rt') as input:
        reader = csv.DictReader(input, delimiter='\t')

        metadata.update({
            'content': 'flightlog',
            'source': 'gnettrack'
        })

        output.write(metadata)

        for row in reader:
            row_ts = row['Timestamp']
            [date, time] = row_ts.split('_')
            [year, month, day] = date.split('.')
            [hour, minute, second] = time.split('.')
            dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            timestamp = int(dt.timestamp() * 1000)
            device = row['DEVICE']

            uaid = {'int': f'{device}:{track_id}'}
            uaid.update(dslice(row, 'IP', 'IMEI', 'IMSI'))

            maybe_float = lambda x: float(x) if x and x != '-' else None
            maybe_int = lambda x: int(x) if x and x != '-' else None

            net_tech = row['NetworkTech']
            net_mode = row['NetworkMode']

            if net_tech == '4G' and net_mode in ('4G', 'LTE'):
                radio = '4GLTE'
            elif net_tech == '5G' and net_mode == 'NR':
                radio = '5GNR'
            else:
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
                {'k': 'ARFCN', 'c': maybe_int}
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

            row_metadata = dslice(
                row,
                'Operatorname',
                'BATTERY',
                'Accuracy',
                'Location',
            )

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
