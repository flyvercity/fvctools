import json
from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.senhive import convert_to_fvc

def test_convert_to_fvc_senhive_writes_expected_ndjson(tmp_path):
    input_path = tmp_path / 'test.senhive'
    # Mixed quotes and no quotes in headers/values to test robustness
    input_path.write_text(
        "'timestamp';'track_id';'vehicle_serial_number';'vehicle_location_lat';'vehicle_location_lon';'altitude_gps (m)'\n"
        "2023-01-01T12:00:00Z;'track_1';'SN1';52.1;4.1;100.1\n"
        "'2023-01-01T12:00:01Z';track_2;SN2;'52.2';'4.2';'100.2'\n",
        encoding='utf-8',
    )

    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'senhive'}
    assert rows[1] == {
        'time': {'unix': 1672574400000},
        'uaid': {'int': 'track_1', 'serial': 'SN1'},
        'pos': {'loc': {'lat': 52.1, 'lon': 4.1, 'alt': 100.1}},
    }
    assert rows[2] == {
        'time': {'unix': 1672574401000},
        'uaid': {'int': 'track_2', 'serial': 'SN2'},
        'pos': {'loc': {'lat': 52.2, 'lon': 4.2, 'alt': 100.2}},
    }

def test_convert_to_fvc_senhive_skips_invalid_rows(tmp_path, caplog):
    import logging

    caplog.set_level(logging.WARNING, logger='fvc.tools.df')

    input_path = tmp_path / 'test_invalid.senhive'
    input_path.write_text(
        "'timestamp';'track_id';'vehicle_serial_number';'vehicle_location_lat';'vehicle_location_lon';'altitude_gps (m)'\n"
        "2023-01-01T12:00:00Z;track_1;SN1;52.1;4.1;100.1\n"
        "2023-01-01T12:00:01Z;track_2;SN2;;4.2;100.2\n", # Missing lat
        encoding='utf-8',
    )

    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]
    assert len(rows) == 2 # Metadata + 1 valid row
    assert "1 invalid rows skipped" in caplog.text
