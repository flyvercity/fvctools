import sys
from unittest.mock import MagicMock, patch

# We need to mock these before importing fvc.tools.render.core if it imports them at top level.
# Using a context manager for the whole module is tricky, but we can patch them for the import.
with patch.dict('sys.modules', {
    'boto3': MagicMock(),
    'benedict': MagicMock(),
    'rich': MagicMock(),
    'rich.live': MagicMock(),
    'rich.spinner': MagicMock(),
    'fvc.tools.df.utils': MagicMock(),
    'fvc.tools.render.templates': MagicMock(),
}):
    from fvc.tools.render.core import calculate_bounds


def test_calculate_bounds_empty():
    """Test calculate_bounds with an empty list."""
    assert calculate_bounds([]) == {'north': 0, 'south': 0, 'east': 0, 'west': 0}


def test_calculate_bounds_single_point():
    """Test calculate_bounds with a single point."""
    coords = [{'lat': 10.0, 'lon': 20.0}]
    expected = {'north': 10.0, 'south': 10.0, 'east': 20.0, 'west': 20.0}
    assert calculate_bounds(coords) == expected


def test_calculate_bounds_multiple_points():
    """Test calculate_bounds with multiple points."""
    coords = [
        {'lat': 10.0, 'lon': 20.0},
        {'lat': 15.0, 'lon': 15.0},
        {'lat': 5.0, 'lon': 25.0},
    ]
    expected = {'north': 15.0, 'south': 5.0, 'east': 25.0, 'west': 15.0}
    assert calculate_bounds(coords) == expected


def test_calculate_bounds_negative_coordinates():
    """Test calculate_bounds with negative coordinates."""
    coords = [
        {'lat': -10.0, 'lon': -20.0},
        {'lat': -15.0, 'lon': -15.0},
        {'lat': -5.0, 'lon': -25.0},
    ]
    expected = {'north': -5.0, 'south': -15.0, 'east': -15.0, 'west': -25.0}
    assert calculate_bounds(coords) == expected


def test_calculate_bounds_mixed_coordinates():
    """Test calculate_bounds with mixed positive and negative coordinates."""
    coords = [
        {'lat': -10.0, 'lon': 20.0},
        {'lat': 15.0, 'lon': -15.0},
    ]
    expected = {'north': 15.0, 'south': -10.0, 'east': 20.0, 'west': -15.0}
    assert calculate_bounds(coords) == expected
