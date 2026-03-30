import sys
from unittest.mock import MagicMock, patch
import logging
import pytest

# Mock dependencies
mock_botobuddy = MagicMock()
mock_botobuddy_utils = MagicMock()

def simple_dslice(source, *args):
    result = {}
    for arg in args:
        key = arg.get('k')
        name = arg.get('n', key)
        if key in source:
            result[name] = source[key]
    return result

mock_botobuddy_utils.dslice = simple_dslice
mock_botobuddy.utils = mock_botobuddy_utils

@pytest.fixture
def get_modem_data_fn():
    with patch.dict('sys.modules', {
        'botobuddy': mock_botobuddy,
        'botobuddy.utils': mock_botobuddy_utils,
    }):
        if 'fvc.tools.df.xformats.manna' in sys.modules:
            del sys.modules['fvc.tools.df.xformats.manna']

        from fvc.tools.df.xformats.manna import _get_modem_data
        yield _get_modem_data

        if 'fvc.tools.df.xformats.manna' in sys.modules:
            del sys.modules['fvc.tools.df.xformats.manna']

def test_get_modem_data_valid(caplog, get_modem_data_fn):
    caplog.set_level(logging.DEBUG, logger='fvc.tools.df')
    row = {
        'modem1': '{"rsrp": -80, "operator_num": 12345, "cell_lac": 100, "cell_tac": 0, "cell_id": 54321}'
    }
    result = get_modem_data_fn(row, 'modem1', 1)

    assert result is not None
    assert result['rsrp'] == -80
    assert result['radio'] == '2G3G'
    assert "Error parsing modem data" not in caplog.text

def test_get_modem_data_invalid_json(caplog, get_modem_data_fn):
    caplog.set_level(logging.DEBUG, logger='fvc.tools.df')
    row = {
        'modem1': '{invalid_json'
    }
    result = get_modem_data_fn(row, 'modem1', 2)

    assert result is None
    assert "Error parsing modem data" in caplog.text
    records = caplog.records
    warning_record = next(r for r in records if "Error parsing modem data" in r.message)
    assert warning_record.levelname == 'WARNING'

def test_get_modem_data_missing_key(caplog, get_modem_data_fn):
    caplog.set_level(logging.DEBUG, logger='fvc.tools.df')
    row = {}
    result = get_modem_data_fn(row, 'modem1', 3)

    assert result is None
    assert "Error parsing modem data" in caplog.text
    records = caplog.records
    warning_record = next(r for r in records if "Error parsing modem data" in r.message)
    assert "'modem1'" in warning_record.message or "modem1" in warning_record.message

def test_get_modem_data_type_error_parsing(caplog, get_modem_data_fn):
    caplog.set_level(logging.DEBUG, logger='fvc.tools.df')
    row = {
        'modem1': None
    }
    result = get_modem_data_fn(row, 'modem1', 4)

    assert result is None
    assert "Error parsing modem data" in caplog.text

def test_get_modem_data_logic_error(caplog, get_modem_data_fn):
    caplog.set_level(logging.DEBUG, logger='fvc.tools.df')
    row = {
        'modem1': '{"operator_num": 12345}'
    }
    result = get_modem_data_fn(row, 'modem1', 5)

    assert result is None
    assert "Error getting modem data" in caplog.text
    records = caplog.records
    error_record = next(r for r in records if "Error getting modem data" in r.message)
    assert error_record.levelname == 'ERROR'
    assert error_record.exc_info is not None
