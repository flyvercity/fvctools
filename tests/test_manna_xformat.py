import sys
from unittest.mock import MagicMock
import logging

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
sys.modules['botobuddy'] = mock_botobuddy
sys.modules['botobuddy.utils'] = mock_botobuddy_utils

import pytest
from fvc.tools.df.xformats.manna import _get_modem_data

def test_get_modem_data_valid(caplog):
    caplog.set_level(logging.DEBUG)
    row = {
        'modem1': '{"rsrp": -80, "operator_num": 12345, "cell_lac": 100, "cell_tac": 0, "cell_id": 54321}'
    }
    result = _get_modem_data(row, 'modem1', 1)

    assert result is not None
    assert result['RSRP'] == -80
    assert result['radio'] == '2G3G'
    assert "Error parsing modem data" not in caplog.text

def test_get_modem_data_invalid_json(caplog):
    caplog.set_level(logging.DEBUG)
    row = {
        'modem1': '{invalid_json'
    }
    result = _get_modem_data(row, 'modem1', 2)

    assert result is None
    assert "Error parsing modem data" in caplog.text
    # Verify it is not an exception log (no traceback)
    # The current implementation uses lg.warning which doesn't print traceback unless exc_info=True
    # We can check the record level
    records = caplog.records
    warning_record = next(r for r in records if "Error parsing modem data" in r.message)
    assert warning_record.levelname == 'WARNING'

def test_get_modem_data_missing_key(caplog):
    caplog.set_level(logging.DEBUG)
    row = {}
    # modem1 is missing
    result = _get_modem_data(row, 'modem1', 3)

    assert result is None
    assert "Error parsing modem data" in caplog.text
    # Specifically check if KeyError is mentioned in the message
    records = caplog.records
    warning_record = next(r for r in records if "Error parsing modem data" in r.message)
    assert "'modem1'" in warning_record.message or "modem1" in warning_record.message

def test_get_modem_data_type_error_parsing(caplog):
    caplog.set_level(logging.DEBUG)
    row = {
        'modem1': None # This will cause TypeError in json.loads
    }
    result = _get_modem_data(row, 'modem1', 4)

    assert result is None
    assert "Error parsing modem data" in caplog.text

def test_get_modem_data_logic_error(caplog):
    caplog.set_level(logging.DEBUG)
    # Missing fields lead to None which causes TypeError in formatting logic later
    # This should be caught by the second try...except block (generic Exception)
    row = {
        'modem1': '{"operator_num": 12345}'
    }
    result = _get_modem_data(row, 'modem1', 5)

    assert result is None
    # This one should be logged as Exception (ERROR) with traceback
    assert "Error getting modem data" in caplog.text
    records = caplog.records
    error_record = next(r for r in records if "Error getting modem data" in r.message)
    assert error_record.levelname == 'ERROR'
    assert error_record.exc_info is not None
