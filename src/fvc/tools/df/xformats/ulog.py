import re
from datetime import datetime, timezone
from pathlib import Path

from pyulog import ULog

from fvc.tools.df.utils import JsonlinesIO, lg


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    ulog = ULog(str(input_path.resolve()))

    filename = input_path.name
    start_dt = extract_datetime_from_filename(filename)
    uaid = filename.split('+')[0]

    if not start_dt:
        lg.warning(
            f'Could not extract datetime from filename {filename}. '
            f'Falling back to boot time.'
        )

        start_dt = datetime.fromtimestamp(
            ulog.start_timestamp / 1e6, tz=timezone.utc
        )

    metadata.update({'content': 'flightlog', 'source': 'ulog'})

    output.write(metadata)

    gps_times = []
    latitudes = []
    longitudes = []
    altitudes = []

    for d in ulog.data_list:
        if d.name == 'vehicle_gps_position':
            gps_times = d.data.get('timestamp', [])
            latitudes = d.data.get('lat', [])
            longitudes = d.data.get('lon', [])
            altitudes = d.data.get('alt', [])

    for i in range(len(gps_times)):
        record = {
            'uaid': {'int': uaid},
            'time': {'unix': int(gps_times[i])},
            'pos': {
                'loc': {
                    'lat': float(latitudes[i] / 1e7),
                    'lon': float(longitudes[i] / 1e7),
                    'height': float(altitudes[i] / 1000.0),
                }
            },
        }
        output.write(record)


def extract_datetime_from_filename(filename):
    """Extracts the datetime from PX4 Ulog filenames."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', filename)

    if not match:
        return None

    date_str, time_str = match.groups()
    datetime_str = f'{date_str} {time_str.replace("-", ":")}'

    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    return dt.replace(tzinfo=timezone.utc)
