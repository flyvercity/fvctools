from pathlib import Path

import pytest
import simplekml

from fvc.tools.df.xformats.geojson import export_from_fvc as export_geojson_from_fvc
from fvc.tools.df.xformats.geojson import generate_point as generate_geojson_point
from fvc.tools.df.xformats.kml import export_from_fvc as export_kml_from_fvc
from fvc.tools.df.xformats.kml import generate_line as generate_kml_line
from fvc.tools.df.xformats.kml import generate_point as generate_kml_point


class InputParam:
    def __init__(self, path: Path):
        self._path = path

    def fetch(self):
        return self._path


def _params(path: Path):
    return {'input': InputParam(path)}


def test_generate_geojson_point_omits_alt_when_missing():
    point = generate_geojson_point({}, {'pos': {'loc': {'lon': 10.0, 'lat': 20.0}}})
    assert point['geometry']['coordinates'] == [10.0, 20.0]


def test_generate_geojson_point_requires_lon_lat():
    with pytest.raises(UserWarning, match='Missing required coordinates'):
        generate_geojson_point({}, {'pos': {'loc': {'lat': 20.0}}})


def test_export_geojson_from_fvc_fails_fast_when_first_record_has_no_lon_lat(tmp_path):
    input_path = tmp_path / 'flightlog.jsonl'
    input_path.write_text(
        '\n'.join(
            [
                '{"content":"flightlog"}',
                '{"pos":{"loc":{"lat":55.0}}}',
                '{"pos":{"loc":{"lon":12.0,"lat":55.0}}}',
            ]
        )
        + '\n',
        encoding='utf-8',
    )

    with pytest.raises(UserWarning, match='Missing required coordinates'):
        export_geojson_from_fvc(_params(input_path), tmp_path / 'output.geojson')


def test_generate_kml_point_omits_alt_when_missing():
    kml = simplekml.Kml()
    generate_kml_point({}, {'pos': {'loc': {'lon': 10.0, 'lat': 20.0}}}, kml)
    assert '<coordinates>10.0,20.0' in kml.kml()
    assert 'None' not in kml.kml()


def test_generate_kml_line_requires_lon_lat():
    curr_pos = {'lon': 10.0, 'lat': 20.0, 'alt': None}
    with pytest.raises(UserWarning, match='Missing required coordinates'):
        generate_kml_line({}, {'pos': {'loc': {'lon': 11.0}}}, curr_pos, simplekml.Kml())


def test_export_kml_from_fvc_fails_fast_when_first_record_has_no_lon_lat(tmp_path):
    input_path = tmp_path / 'flightlog.jsonl'
    input_path.write_text(
        '\n'.join(
            [
                '{"content":"flightlog"}',
                '{"pos":{"loc":{"lat":55.0}}}',
                '{"pos":{"loc":{"lon":12.0,"lat":55.0}}}',
            ]
        )
        + '\n',
        encoding='utf-8',
    )

    with pytest.raises(UserWarning, match='Missing required coordinates'):
        export_kml_from_fvc(_params(input_path), tmp_path / 'output.kmz')
