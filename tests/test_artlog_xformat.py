import json

import pytest

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.artlog import convert_to_fvc


def test_convert_to_fvc_artlog_writes_expected_ndjson(tmp_path):
    input_path = tmp_path / 'test.artlog'
    input_path.write_text(
        'Timestamp_nsec TrackUUID Latitude Longitude Altitude TimeZone\n'
        '1710000000123456 abc123 55.0 12.0 120.5 UTC\n'
        '1710000001123456 abc123 55.0001 12.0001 121.5 UTC\n',
        encoding='utf-8',
    )

    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'artlog'}
    assert rows[1:] == [
        {
            'time': {'unix': 1710000000},
            'uaid': {'int': 'abc123'},
            'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
        },
        {
            'time': {'unix': 1710000001},
            'uaid': {'int': 'abc123'},
            'pos': {'loc': {'lat': 55.0001, 'lon': 12.0001, 'alt': 121.5}},
        },
    ]


def test_convert_to_fvc_artlog_raises_when_timezone_is_not_utc(tmp_path):
    input_path = tmp_path / 'test.artlog'
    input_path.write_text(
        'Timestamp_nsec TrackUUID Latitude Longitude Altitude TimeZone\n1710000000123456 abc123 55.0 12.0 120.5 CET\n',
        encoding='utf-8',
    )

    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        with pytest.raises(ValueError, match='TimeZone set to UTC'):
            convert_to_fvc({}, {}, input_path, output)
