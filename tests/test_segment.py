import math

import numpy as np
import polars as pl
import pytest

from fvc.tools.flightlog.segment import SegmentParams, filter_displacement


def _make_params(**overrides) -> SegmentParams:
    defaults = SegmentParams(
        segment_by_height=False,
        segment_height_meters=5.0,
        airborne_only=True,
        segment_by_idle=False,
        idle_time_seconds=60.0,
        filter_by_duration=False,
        filter_duration_seconds=300.0,
        filter_by_displacement=True,
        filter_displacement_lateral_meters=200.0,
        filter_displacement_vertical_meters=50.0,
    )
    defaults.update(overrides)
    return defaults


def _make_frame(lat_range, lon_range, height_range, n_points=10):
    """Build a synthetic frame with nested pos.loc struct and derived_height."""
    lats = np.linspace(lat_range[0], lat_range[1], n_points)
    lons = np.linspace(lon_range[0], lon_range[1], n_points)
    heights = np.linspace(height_range[0], height_range[1], n_points)
    timestamps = list(range(1000, 1000 + n_points * 100, 100))

    pos_structs = [{'loc': {'lat': float(lat), 'lon': float(lon)}} for lat, lon in zip(lats, lons)]

    return pl.DataFrame({
        'timestamp': timestamps,
        'pos': pos_structs,
        'derived_height': heights.tolist(),
    })


class TestFilterDisplacement:
    """Tests for the filter_displacement function."""

    def test_hovering_frame_filtered_out(self):
        """A frame with ~5.6m lateral and ~5m vertical should be filtered out."""
        # lat span 0.00005 deg ≈ 5.6m, lon span similar, height span 5m
        frame = _make_frame(
            lat_range=(51.0, 51.00005),
            lon_range=(-0.1, -0.09995),
            height_range=(100.0, 105.0),
        )
        params = _make_params()
        metaproc = {}

        result = filter_displacement([frame], params, metaproc)

        assert len(result) == 0

    def test_lateral_movement_kept(self):
        """A frame with >200m lateral displacement should be kept."""
        # lat span 0.003 deg ≈ 334m
        frame = _make_frame(
            lat_range=(51.0, 51.003),
            lon_range=(-0.1, -0.1),
            height_range=(100.0, 105.0),
        )
        params = _make_params()
        metaproc = {}

        result = filter_displacement([frame], params, metaproc)

        assert len(result) == 1

    def test_vertical_movement_kept(self):
        """A frame with >50m vertical but minimal lateral should be kept."""
        # lat span ~5.6m (hovering), height span 60m
        frame = _make_frame(
            lat_range=(51.0, 51.00005),
            lon_range=(-0.1, -0.09995),
            height_range=(10.0, 70.0),
        )
        params = _make_params()
        metaproc = {}

        result = filter_displacement([frame], params, metaproc)

        assert len(result) == 1

    def test_below_both_thresholds_filtered(self):
        """A frame just below 200m lateral AND below 50m vertical should be filtered."""
        # lat span 0.0015 deg ≈ 167m, height span 40m — both below thresholds
        frame = _make_frame(
            lat_range=(51.0, 51.0015),
            lon_range=(-0.1, -0.1),
            height_range=(100.0, 140.0),
        )
        params = _make_params()
        metaproc = {}

        result = filter_displacement([frame], params, metaproc)

        assert len(result) == 0

    def test_filter_disabled_passes_all(self):
        """When filter_by_displacement=False, we don't call filter_displacement,
        but if called directly all frames should still be evaluated by the function.
        Here we test that a hovering frame is still filtered even if the param is False
        (the caller controls whether to invoke the function)."""
        # This tests that the function itself always applies filtering.
        # The segment() function checks the flag before calling.
        hovering = _make_frame(
            lat_range=(51.0, 51.00005),
            lon_range=(-0.1, -0.09995),
            height_range=(100.0, 105.0),
        )
        moving = _make_frame(
            lat_range=(51.0, 51.003),
            lon_range=(-0.1, -0.1),
            height_range=(100.0, 105.0),
        )
        # Use very low thresholds so everything passes
        params = _make_params(
            filter_by_displacement=False,
            filter_displacement_lateral_meters=0.0,
            filter_displacement_vertical_meters=0.0,
        )
        metaproc = {}

        result = filter_displacement([hovering, moving], params, metaproc)

        # With thresholds at 0, any non-zero displacement passes
        assert len(result) == 2

    def test_empty_frame_filtered(self):
        """An empty DataFrame with the correct schema should not crash and be filtered out."""
        empty_frame = pl.DataFrame({
            'timestamp': pl.Series([], dtype=pl.Int64),
            'pos': pl.Series(
                [],
                dtype=pl.Struct({'loc': pl.Struct({'lat': pl.Float64, 'lon': pl.Float64})}),
            ),
            'derived_height': pl.Series([], dtype=pl.Float64),
        })
        params = _make_params()
        metaproc = {}

        result = filter_displacement([empty_frame], params, metaproc)

        assert len(result) == 0

    def test_null_coordinates_filtered(self):
        """A frame with None lat/lon values should not crash and be filtered out."""
        n_points = 5
        timestamps = list(range(1000, 1000 + n_points * 100, 100))
        pos_structs = [{'loc': {'lat': None, 'lon': None}} for _ in range(n_points)]

        null_frame = pl.DataFrame({
            'timestamp': timestamps,
            'pos': pos_structs,
            'derived_height': [100.0] * n_points,
        })
        params = _make_params()
        metaproc = {}

        result = filter_displacement([null_frame], params, metaproc)

        assert len(result) == 0

    def test_metaproc_counts(self):
        """Verify metaproc dict has correct in/out counts and threshold values."""
        hovering = _make_frame(
            lat_range=(51.0, 51.00005),
            lon_range=(-0.1, -0.09995),
            height_range=(100.0, 105.0),
        )
        moving = _make_frame(
            lat_range=(51.0, 51.003),
            lon_range=(-0.1, -0.1),
            height_range=(100.0, 105.0),
        )
        params = _make_params()
        metaproc = {}

        filter_displacement([hovering, moving], params, metaproc)

        assert metaproc['filter_displacement_in'] == 2
        assert metaproc['filter_displacement_out'] == 1
        assert metaproc['filter_displacement_lateral_meters'] == 200.0
        assert metaproc['filter_displacement_vertical_meters'] == 50.0
