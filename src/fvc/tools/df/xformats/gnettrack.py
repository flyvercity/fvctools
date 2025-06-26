from pathlib import Path
import csv
from datetime import datetime
import uuid

from fvc.tools.df.util import JsonlinesIO, dslice


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

            maybe_float = lambda x: float(x) if x else None
            maybe_int = lambda x: int(x) if x else None

            cellsig = dslice(
                row,
                {'k': 'NetworkTech', 'd': 'unknown', 'n': 'radio'},
                {'k': 'CSI_PCI', 'c': maybe_float, 'd': 0.0, 'n': 'CSI-RSRP'},
                {'k': 'CSI_RSRQ', 'c': maybe_float, 'd': 0.0, 'n': 'CSI-RSRQ'},
                {'k': 'CSI_RSSI', 'c': maybe_float, 'd': 0.0, 'n': 'CSI-RSSI'},
            )

            loc = dslice(
                row,
                {'k': 'Latitude', 'c': maybe_float, 'n': 'lat'},
                {'k': 'Longitude', 'c': maybe_float, 'n': 'lon'}
            )

            datalink = dslice(
                row,
                {'k': 'PINGMAX', 'c': maybe_int, 'n': 'rtt'},
                {'k': 'PINGLOSS', 'c': maybe_int, 'n': 'loss'}
            )

            row_metadata = dslice(row, 'Operatorname', 'BATTERY')

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
