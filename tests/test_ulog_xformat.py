import json
from unittest.mock import patch

import pytest

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.ulog import convert_to_fvc


class _MockDataset:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class _MockULog:
    def __init__(self):
        self.start_timestamp = 0
        self.data_list = [
            _MockDataset(
                'vehicle_gps_position',
                {
                    'timestamp': [1710000000123456, 1710000001123456],
                    'lat': [550000000, 550000100],
                    'lon': [120000000, 120000100],
                    'alt': [12345, 12500],
                },
            )
        ]


def test_convert_to_fvc_ulog_writes_expected_ndjson(tmp_path):
    input_path = tmp_path / '123+2024-01-01_00-00-00.ulg'
    input_path.write_text('', encoding='utf-8')
    output_path = tmp_path / 'out.fvc'

    with patch('fvc.tools.df.xformats.ulog.ULog', return_value=_MockULog()):
        with JsonlinesIO(output_path, 'w') as output:
            convert_to_fvc({}, {}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert rows[0] == {'content': 'flightlog', 'source': 'ulog'}
    assert [row['uaid'] for row in rows[1:]] == [{'int': '123'}, {'int': '123'}]
    assert [row['time'] for row in rows[1:]] == [{'unix': 1710000000123456}, {'unix': 1710000001123456}]
    assert rows[1]['pos']['loc']['lat'] == pytest.approx(55.0)
    assert rows[1]['pos']['loc']['lon'] == pytest.approx(12.0)
    assert rows[1]['pos']['loc']['height'] == pytest.approx(12.345)
    assert rows[2]['pos']['loc']['lat'] == pytest.approx(55.00001)
    assert rows[2]['pos']['loc']['lon'] == pytest.approx(12.00001)
    assert rows[2]['pos']['loc']['height'] == pytest.approx(12.5)
