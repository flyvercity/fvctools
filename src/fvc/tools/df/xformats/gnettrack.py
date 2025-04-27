
from pathlib import Path
import csv
from datetime import datetime
import uuid

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
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            device = row['DEVICE']
            ipaddr = row['IP']

            uaid = {'int': f'{device}:{track_id}'}

            if ipaddr := row['IP']:
                uaid['ip'] = ipaddr

            if imei := row['IMEI']:
                uaid['imei'] = imei

            if imsi := row['IMSI']:
                uaid['imsi'] = imsi

            radio = row['NetworkTech']
            rsrp = float(row['CSI_RSRP'])
            rsrq = float(row['CSI_RSRQ'])

            cellsig = {
                'radio': radio,
                'RSRP': rsrp,
                'RSRQ': rsrq
            }

            record = {
                'time': {
                    'unix': timestamp,
                    'original': row_ts
                },
                'pos': {
                    'loc': {
                        'lat': lat,
                        'lon': lon
                    }
                },
                'cellsig': cellsig
            }

            if uaid:
                record['uaid'] = uaid

            output.write(record)
