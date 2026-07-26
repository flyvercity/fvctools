import json
from unittest.mock import MagicMock, patch

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.safirmqtt import convert_to_fvc as convert_v1
from fvc.tools.df.xformats.safirmqtt_v2 import convert_to_fvc as convert_v2


@patch('fvc.tools.df.xformats.safirmqtt.geoid.load_geoid')
@patch('fvc.tools.df.xformats.safirmqtt.geoid.amsl_to_ellipsoidal')
def test_convert_safirmqtt_v1(mock_amsl_to_ellipsoidal, mock_load_geoid, tmp_path):
    mock_load_geoid.return_value = MagicMock()
    mock_amsl_to_ellipsoidal.return_value = 150.0

    input_path = tmp_path / 'test_v1.jsonl'
    input_path.write_text(
        json.dumps(
            {
                'version': '1',
                'timestamp': '2023-01-01T12:00:00Z',
                'identifiers': [
                    {'version': '1', 'system': 'ICAOHex', 'key': '123'},
                    {'version': '1', 'system': 'Other', 'key': '456'},
                ],
                'location': {'version': '1', 'latitude': 55.0, 'longitude': 12.0, 'altitudeAMSL': 100.0},
                'origin': 'test-origin',
            }
        )
        + '\n',
        encoding='utf-8',
    )

    output_path = tmp_path / 'out_v1.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_v1({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert len(rows) == 2
    assert rows[0]['content'] == 'flightlog'
    assert rows[0]['source'] == 'safirmqtt'
    assert rows[1]['time']['unix'] == 1672574400000  # 2023-01-01 12:00:00 UTC in ms
    assert rows[1]['uaid'] == {'icaohex': '123', 'int': '456'}
    assert rows[1]['pos'] == {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 150.0}}
    assert rows[1]['origin'] == 'test-origin'


@patch('fvc.tools.df.xformats.safirmqtt_v2.geoid.load_geoid')
@patch('fvc.tools.df.xformats.safirmqtt_v2.geoid.amsl_to_ellipsoidal')
def test_convert_safirmqtt_v2(mock_amsl_to_ellipsoidal, mock_load_geoid, tmp_path):
    mock_load_geoid.return_value = MagicMock()
    mock_amsl_to_ellipsoidal.return_value = 250.0

    input_path = tmp_path / 'test_v2.jsonl'
    input_path.write_text(
        json.dumps({'content': 'capture.message'})
        + '\n'
        + json.dumps(
            {
                'payload': {
                    'timestamp': '2023-01-01T12:00:00Z',
                    'identifiers': [{'system': 'ICAOHex', 'key': '123'}, {'system': 'Other', 'key': '456'}],
                    'location': {'latitude': 55.0, 'longitude': 12.0, 'altitudeAMSL': 200.0},
                    'origin': 'test-origin-v2',
                }
            }
        )
        + '\n',
        encoding='utf-8',
    )

    output_path = tmp_path / 'out_v2.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_v2({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert len(rows) == 2
    assert rows[0]['content'] == 'flightlog'
    assert rows[0]['source'] == 'safirmqtt'
    assert rows[1]['time']['unix'] == 1672574400000
    assert rows[1]['uaid'] == {'icaohex': '123', 'int': '456'}
    assert rows[1]['pos'] == {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 250.0}}
    assert rows[1]['origin'] == 'test-origin-v2'
