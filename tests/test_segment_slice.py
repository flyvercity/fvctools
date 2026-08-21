import pytest
import polars as pl
from benedict import benedict

from fvc.tools.flightlog.load import FlightlogDataset
from fvc.tools.flightlog.segment import slice_segments


def _make_dataset(n_frames: int) -> FlightlogDataset:
    """Build a FlightlogDataset with n distinguishable frames."""
    frames = []
    for i in range(n_frames):
        base_ts = i * 1000
        frames.append(pl.DataFrame({
            'timestamp': [base_ts, base_ts + 1, base_ts + 2],
            'value': [float(i)] * 3,
        }))
    return FlightlogDataset(
        metadata=benedict({'content': 'flightlog'}),
        frames=frames,
    )


class TestSliceSegments:
    def test_select_segments_keeps_specified(self):
        ds = _make_dataset(5)
        result = slice_segments(ds, select_segments=[0, 2, 4])
        assert len(result.frames) == 3
        assert result.frames[0]['value'][0] == 0.0
        assert result.frames[1]['value'][0] == 2.0
        assert result.frames[2]['value'][0] == 4.0

    def test_select_segments_deduplicates_and_sorts(self):
        ds = _make_dataset(5)
        result = slice_segments(ds, select_segments=[4, 2, 2, 0])
        assert len(result.frames) == 3
        assert result.frames[0]['value'][0] == 0.0
        assert result.frames[1]['value'][0] == 2.0
        assert result.frames[2]['value'][0] == 4.0

    def test_drop_segments_removes_specified(self):
        ds = _make_dataset(5)
        result = slice_segments(ds, drop_segments=[1, 3])
        assert len(result.frames) == 3
        assert result.frames[0]['value'][0] == 0.0
        assert result.frames[1]['value'][0] == 2.0
        assert result.frames[2]['value'][0] == 4.0

    def test_drop_segments_deduplicates(self):
        ds = _make_dataset(5)
        result = slice_segments(ds, drop_segments=[1, 1, 3])
        assert len(result.frames) == 3
        assert result.frames[0]['value'][0] == 0.0
        assert result.frames[1]['value'][0] == 2.0
        assert result.frames[2]['value'][0] == 4.0

    def test_both_set_raises_value_error(self):
        ds = _make_dataset(3)
        with pytest.raises(ValueError, match='mutually exclusive'):
            slice_segments(ds, select_segments=[0], drop_segments=[1])

    def test_select_out_of_range_raises_index_error(self):
        ds = _make_dataset(3)
        with pytest.raises(IndexError, match='Segment index 5 out of range'):
            slice_segments(ds, select_segments=[5])

    def test_drop_out_of_range_raises_index_error(self):
        ds = _make_dataset(3)
        with pytest.raises(IndexError, match='Segment index 5 out of range'):
            slice_segments(ds, drop_segments=[5])

    def test_neither_set_passes_all(self):
        ds = _make_dataset(5)
        result = slice_segments(ds)
        assert result is ds  # No evolve, same object

    def test_drop_all_raises_value_error(self):
        ds = _make_dataset(3)
        with pytest.raises(ValueError, match='0 output frames'):
            slice_segments(ds, drop_segments=[0, 1, 2])

    def test_select_empty_list_raises_value_error(self):
        ds = _make_dataset(3)
        with pytest.raises(ValueError, match='0 output frames'):
            slice_segments(ds, select_segments=[])
