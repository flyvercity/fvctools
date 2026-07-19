import json
import pytest
from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.datcon import convert_to_fvc


def test_convert_to_fvc_datcon_with_guid(tmp_path):
    input_path = tmp_path / 'test.datcon'
    # DJI Datcon header can have parenthesis
    input_path.write_text(
        'TS(ns) TZ GUID ID Latitude(deg) Longitude(deg) Altitude(m)\n'
        '1710000000123456 UTC my-guid-123 my-id-456 55.0 12.0 120.5\n'
        '1710000001123456 UTC my-guid-123 my-id-456 55.0001 12.0001 121.5\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'datcon'}
    assert rows[1:] == [
        {
            'time': {'unix': 1710000000},
            'uaid': {'int': 'my-guid-123'},
            'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
        },
        {
            'time': {'unix': 1710000001},
            'uaid': {'int': 'my-guid-123'},
            'pos': {'loc': {'lat': 55.0001, 'lon': 12.0001, 'alt': 121.5}},
        },
    ]


def test_convert_to_fvc_datcon_fallback_to_id(tmp_path):
    input_path = tmp_path / 'test.datcon'
    input_path.write_text(
        'TS TZ GUID ID Latitude Longitude Altitude\n1710000000123456 UTC N/A my-id-456 55.0 12.0 120.5\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert rows[1] == {
        'time': {'unix': 1710000000},
        'uaid': {'int': 'my-id-456'},
        'pos': {'loc': {'lat': 55.0, 'lon': 12.0, 'alt': 120.5}},
    }


def test_convert_to_fvc_datcon_raises_non_utc(tmp_path):
    input_path = tmp_path / 'test.datcon'
    input_path.write_text(
        'TS TZ GUID ID Latitude Longitude Altitude\n1710000000123456 CET my-guid-123 my-id-456 55.0 12.0 120.5\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        with pytest.raises(AssertionError):
            convert_to_fvc({}, {}, input_path, output)


def test_convert_to_fvc_datcon_header_only(tmp_path):
    input_path = tmp_path / 'test.datcon'
    input_path.write_text(
        'TS TZ GUID ID Latitude Longitude Altitude\n',
        encoding='utf-8',
    )
    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]
    assert len(rows) == 1
    assert rows[0] == {'origin': 'unit-test', 'content': 'flightlog', 'source': 'datcon'}


def test_convert_to_fvc_datcon_empty_file(tmp_path):
    input_path = tmp_path / 'test.datcon'
    input_path.write_text('', encoding='utf-8')
    output_path = tmp_path / 'out.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {}, input_path, output)

    # Output file should be empty (or only containing metadata, but original code returns immediately on empty header)
    assert output_path.read_text(encoding='utf-8') == ''
