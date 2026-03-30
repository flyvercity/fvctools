import pytest
from datetime import datetime, timezone
from dateutil.parser import ParserError


def test_datestring_to_ts_naive():
    """Test with a naive date string (assumed UTC)."""
    # Import inside the test to ensure mocks are active
    from fvc.tools.utils import datestring_to_ts

    datestr = "2023-01-01 12:00:00"
    ts = datestring_to_ts(datestr)
    # 2023-01-01 12:00:00 UTC
    expected_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expected_ts = int(expected_dt.timestamp() * 1000)
    assert ts == expected_ts

def test_datestring_to_ts_utc_aware():
    """Test with an aware date string in UTC."""
    from fvc.tools.utils import datestring_to_ts

    datestr = "2023-01-01 12:00:00+00:00"
    ts = datestring_to_ts(datestr)
    expected_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expected_ts = int(expected_dt.timestamp() * 1000)
    assert ts == expected_ts

def test_datestring_to_ts_non_utc_aware():
    """Test with an aware date string in non-UTC timezone."""
    from fvc.tools.utils import datestring_to_ts

    # 13:00 UTC+1 is 12:00 UTC
    datestr = "2023-01-01 13:00:00+01:00"
    ts = datestring_to_ts(datestr)
    expected_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expected_ts = int(expected_dt.timestamp() * 1000)
    assert ts == expected_ts

def test_datestring_to_ts_iso_format():
    """Test with ISO 8601 format."""
    from fvc.tools.utils import datestring_to_ts

    datestr = "2023-01-01T12:00:00Z"
    ts = datestring_to_ts(datestr)
    expected_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expected_ts = int(expected_dt.timestamp() * 1000)
    assert ts == expected_ts

def test_datestring_to_ts_invalid():
    """Test with invalid date string."""
    from fvc.tools.utils import datestring_to_ts

    with pytest.raises(ParserError):
         datestring_to_ts("not a date")
