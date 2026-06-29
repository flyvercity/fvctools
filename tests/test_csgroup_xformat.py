import json

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.csgroup import convert_to_fvc

def test_convert_to_fvc_csgroup_writes_expected_ndjson(tmp_path):
    input_path = tmp_path / 'test.csgroup'
    input_path.write_text(
        'event_type,datetime_ms,track_id,latitude,longitude,altitude\n'
        'TRACK,1710000000123,abc123,55.0,12.0,120.5\n'
        'OTHER,1710000000124,abc123,55.0,12.0,120.5\n'
        'TRACK,1710000001123,abc123,55.0001,12.0001,121.5\n',
        encoding='utf-8',
    )

    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'csgroup'}
    assert len(rows) == 3
    assert rows[1] == {
        'time': {'unix': 1710000000123},
        'uaid': {'int': 'abc123'},
        'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
    }
    assert rows[2] == {
        'time': {'unix': 1710000001123},
        'uaid': {'int': 'abc123'},
        'pos': {'loc': {'lat': 55.0001, 'lon': 12.0001, 'alt': 121.5}},
    }
