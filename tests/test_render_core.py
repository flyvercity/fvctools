import json
from unittest.mock import MagicMock, patch

# We need to mock these before importing fvc.tools.render.core if it imports them at top level.
# Using a context manager for the whole module is tricky, but we can patch them for the import.
with patch.dict('sys.modules', {
    'boto3': MagicMock(),
    'benedict': MagicMock(),
    'rich': MagicMock(),
    'rich.live': MagicMock(),
    'rich.spinner': MagicMock(),
    'fvc.tools.df.utils': MagicMock(JsonlinesIO=MagicMock()),
    'fvc.tools.render.templates': MagicMock(),
}):
    import fvc.tools.render.core as render_core


class FakeJsonlinesIO:
    last_kwargs = None

    def __init__(self, filepath, mode, raw=False):
        self.filepath = filepath
        FakeJsonlinesIO.last_kwargs = {'mode': mode, 'raw': raw}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def iterate(self):
        with self.filepath.open('rt', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def write_jsonlines(path, records):
    path.write_text(''.join(json.dumps(record) + '\n' for record in records), encoding='utf-8')


def test_calculate_bounds_empty():
    """Test calculate_bounds with an empty list."""
    assert render_core.calculate_bounds([]) == {'north': 0, 'south': 0, 'east': 0, 'west': 0}


def test_calculate_bounds_single_point():
    """Test calculate_bounds with a single point."""
    coords = [{'lat': 10.0, 'lon': 20.0}]
    expected = {'north': 10.0, 'south': 10.0, 'east': 20.0, 'west': 20.0}
    assert render_core.calculate_bounds(coords) == expected


def test_calculate_bounds_multiple_points():
    """Test calculate_bounds with multiple points."""
    coords = [
        {'lat': 10.0, 'lon': 20.0},
        {'lat': 15.0, 'lon': 15.0},
        {'lat': 5.0, 'lon': 25.0},
    ]
    expected = {'north': 15.0, 'south': 5.0, 'east': 25.0, 'west': 15.0}
    assert render_core.calculate_bounds(coords) == expected


def test_calculate_bounds_negative_coordinates():
    """Test calculate_bounds with negative coordinates."""
    coords = [
        {'lat': -10.0, 'lon': -20.0},
        {'lat': -15.0, 'lon': -15.0},
        {'lat': -5.0, 'lon': -25.0},
    ]
    expected = {'north': -5.0, 'south': -15.0, 'east': -15.0, 'west': -25.0}
    assert render_core.calculate_bounds(coords) == expected


def test_calculate_bounds_mixed_coordinates():
    """Test calculate_bounds with mixed positive and negative coordinates."""
    coords = [
        {'lat': -10.0, 'lon': 20.0},
        {'lat': 15.0, 'lon': -15.0},
    ]
    expected = {'north': 15.0, 'south': -10.0, 'east': 20.0, 'west': -15.0}
    assert render_core.calculate_bounds(coords) == expected


def test_extract_coordinates_raw_path_and_cellsig(tmp_path, monkeypatch):
    """Test extract_coordinates reads raw records and includes optional cellsig metadata."""
    fvc_path = tmp_path / 'sample.fvc'
    write_jsonlines(
        fvc_path,
        [
            {
                'pos': {'loc': {'lat': '10.5', 'lon': '20.25', 'alt': 50, 'amsl': 150, 'height': 25}},
                'time': {'unix': 1000},
                'cellsig': {'RSRP': -101, 'RSRQ': -13, 'plmnid': '12345', 'plmnname': 'TestNet'},
            },
            {'pos': {'loc': {'lat': 11, 'lon': 21}}, 'time': {'unix': 2000}},
            {'pos': {'foo': 'bar'}},
        ],
    )
    monkeypatch.setattr(render_core, 'JsonlinesIO', FakeJsonlinesIO)

    coordinates = render_core.extract_coordinates(fvc_path)

    assert FakeJsonlinesIO.last_kwargs == {'mode': 'r', 'raw': True}
    assert coordinates == [
        {
            'lat': 10.5,
            'lon': 20.25,
            'time': 1000,
            'altitude': 50,
            'amsl': 150,
            'height': 25,
            'rsrp': -101,
            'rsrq': -13,
            'plmnid': '12345',
            'plmnname': 'TestNet',
        },
        {
            'lat': 11.0,
            'lon': 21.0,
            'time': 2000,
            'altitude': None,
            'amsl': None,
            'height': None,
        },
    ]


def test_extract_coordinates_handles_malformed_data(tmp_path, monkeypatch):
    """Test extract_coordinates skips bad coordinates and safely handles non-mapping time."""
    fvc_path = tmp_path / 'invalid.fvc'
    write_jsonlines(
        fvc_path,
        [
            {'pos': {'loc': {'lat': 'invalid', 'lon': 20}}, 'time': {'unix': 1}},
            {'pos': {'loc': {'lat': 12.5, 'lon': '22.5'}}, 'time': None},
            {'pos': {'loc': {'lat': 13.5, 'lon': '23.5'}}, 'time': 'not-a-dict'},
        ],
    )
    monkeypatch.setattr(render_core, 'JsonlinesIO', FakeJsonlinesIO)

    coordinates = render_core.extract_coordinates(fvc_path)

    assert coordinates == [
        {
            'lat': 12.5,
            'lon': 22.5,
            'time': None,
            'altitude': None,
            'amsl': None,
            'height': None,
        },
        {
            'lat': 13.5,
            'lon': 23.5,
            'time': None,
            'altitude': None,
            'amsl': None,
            'height': None,
        },
    ]
