import pytest

from fvc.tools.df.xformats.safirmqtt import from_safir_ids as from_safir_ids_v1
from fvc.tools.df.xformats.safirmqtt_v2 import from_safir_ids as from_safir_ids_v2


def test_safirmqtt_from_safir_ids_v1_version_mismatch():
    # v1 raises UserWarning if version != '1'
    with pytest.raises(UserWarning, match='Unsupported version 2 in SAFIR ID'):
        from_safir_ids_v1([{'version': '2', 'system': 'ICAOHex', 'key': '1234'}])


def test_safirmqtt_from_safir_ids_all_systems():
    safir_ids = [
        {'version': '1', 'system': 'ICAOHex', 'key': '400BEE'},
        {'version': '1', 'system': 'ICAORegistration', 'key': 'G-ABCD'},
        {'version': '1', 'system': 'CallSign', 'key': 'BAW123'},
        {'version': '1', 'system': 'Other', 'key': 'INT-1234'},
    ]

    expected = {
        'icaohex': '400BEE',
        'icaoreg': 'G-ABCD',
        'atm': 'BAW123',
        'int': 'INT-1234',
    }

    assert from_safir_ids_v1(safir_ids) == expected
    # v2 does not enforce version checking, but behaves the same for valid records
    assert from_safir_ids_v2(safir_ids) == expected


def test_safirmqtt_from_safir_ids_fallback():
    safir_ids = [
        {'version': '1', 'system': 'ICAOHex', 'key': '400BEE'},
        {'version': '1', 'system': 'ICAORegistration', 'key': 'G-ABCD'},
        {'version': '1', 'system': 'CallSign', 'key': 'BAW123'},
    ]

    expected = {
        'icaohex': '400BEE',
        'icaoreg': 'G-ABCD',
        'atm': 'BAW123',
        'int': '400BEE',  # Fallback to key of first id
    }

    assert from_safir_ids_v1(safir_ids) == expected
    assert from_safir_ids_v2(safir_ids) == expected


def test_safirmqtt_from_safir_ids_empty():
    assert from_safir_ids_v1([]) == {}
    assert from_safir_ids_v2([]) == {}
