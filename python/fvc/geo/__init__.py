import os
from itertools import tee

import pandas
import geopandas

from fvc.df.util import fetch_input_file, JsonlinesIO


def fetch_geodata(file_name: str) -> geopandas.GeoDataFrame:
    file_path = fetch_input_file({'cache_dir': os.getenv('FVC_CACHE')}, file_name)

    with JsonlinesIO(file_path, 'r') as io:
        metadata = io.read()
        assert metadata and metadata['content'] == 'flightlog'

        def fetch(r):
            return (
                r['time']['unix'],
                r['uaid']['int'],
                r['pos']['loc']['lat'],
                r['pos']['loc']['lon']
            )

        tuples = map(fetch, io.iterate())
        lists = list(zip(*tuples))

        df = pandas.DataFrame({
            'Time': lists[0],
            'ID': lists[1],
            'Latitude': lists[2],
            'Longitude': lists[3]
        })

    gdf = geopandas.GeoDataFrame(                    # type: ignore
        df,
        geometry=geopandas.points_from_xy(df.Longitude, df.Latitude),
        crs="EPSG:4326"
    )

    return gdf
