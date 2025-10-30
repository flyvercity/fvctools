import os
from pathlib import Path

import geopandas
import pandas

from fvc.tools.df.utils import JsonlinesIO


def fetch_geodata(file_name: str) -> geopandas.GeoDataFrame:
    input = Path(os.getenv('FVC_CACHE'), file_name)

    with JsonlinesIO(input.fetch(), 'r') as io:
        metadata = io.read()
        assert metadata and metadata['content'] == 'flightlog'

        def fetch(r):
            return (
                r.get('time.unix'),
                r.get('uaid.int'),
                r.get('pos.loc.lat'),
                r.get('pos.loc.lon'),
                r.get('pos.loc.alt'),
            )

        tuples = map(fetch, io.iterate())
        lists = list(zip(*tuples))

        df = pandas.DataFrame(
            {
                'Time': lists[0],
                'ID': lists[1],
                'Latitude': lists[2],
                'Longitude': lists[3],
                'Altitude': lists[4],
            }
        )

    gdf = geopandas.GeoDataFrame(  # type: ignore
        df,
        geometry=geopandas.points_from_xy(
            df.Longitude, df.Latitude, z=df.Altitude
        ),
        crs='EPSG:4326',
    )

    return gdf
