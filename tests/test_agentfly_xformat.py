import json
from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.agentfly import convert_to_fvc


def test_convert_to_fvc_agentfly_comma_delimiter(tmp_path):
    input_path = tmp_path / 'test.csv'
    input_path.write_text(
        '#unix_timestamp,flight_id,latitude_deg,longitude_deg,altitude_m,source_id,origin\n'
        '1710000000,abc123,55.0,12.0,120.5,sensor1,origin1\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'
    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]
    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'agentfly'}
    assert rows[1] == {
        'time': {'unix': 1710000000},
        'uaid': {'int': 'abc123'},
        'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
        'sensor': 'sensor1',
        'origin': 'origin1',
    }


def test_convert_to_fvc_agentfly_semicolon_delimiter(tmp_path):
    input_path = tmp_path / 'test.csv'
    input_path.write_text(
        '#unix_timestamp;flight_id;latitude_deg;longitude_deg;altitude_m;source_id;origin\n'
        '1710000000;abc123;55.0;12.0;120.5;sensor1;origin1\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'
    params = {'custom': ['use-semicolon']}
    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc(params, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]
    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'agentfly'}
    assert rows[1] == {
        'time': {'unix': 1710000000},
        'uaid': {'int': 'abc123'},
        'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
        'sensor': 'sensor1',
        'origin': 'origin1',
    }


def test_convert_to_fvc_agentfly_no_origin(tmp_path):
    input_path = tmp_path / 'test.csv'
    input_path.write_text(
        '#unix_timestamp,flight_id,latitude_deg,longitude_deg,altitude_m,source_id\n'
        '1710000000,abc123,55.0,12.0,120.5,sensor1\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'
    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]
    assert rows[1] == {
        'time': {'unix': 1710000000},
        'uaid': {'int': 'abc123'},
        'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
        'sensor': 'sensor1',
    }
