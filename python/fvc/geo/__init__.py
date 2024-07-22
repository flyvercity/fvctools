import os
from itertools import tee

import pandas
import geopandas

from fvc.df.util import InputFile, JsonlinesIO, JsonQuery


def fetch_geodata(file_name: str) -> geopandas.GeoDataFrame:
    input = InputFile({'cache_dir': os.getenv('FVC_CACHE')}, file_name)

    qtime = JsonQuery('time.unix')
    quaid = JsonQuery('uaid.int', 'unknown')
    qlat = JsonQuery('pos.loc.lat')
    qlon = JsonQuery('pos.loc.lon')
    qalt = JsonQuery('pos.loc.alt')

    with JsonlinesIO(input.fetch(), 'r') as io:
        metadata = io.read()
        assert metadata and metadata['content'] == 'flightlog'

        def fetch(r):
            return (qtime(r), quaid(r), qlat(r), qlon(r), qalt(r))

        tuples = map(fetch, io.iterate())
        lists = list(zip(*tuples))

        df = pandas.DataFrame({
            'Time': lists[0],
            'ID': lists[1],
            'Latitude': lists[2],
            'Longitude': lists[3],
            'Altitude': lists[4]
        })

    gdf = geopandas.GeoDataFrame(                    # type: ignore
        df,
        geometry=geopandas.points_from_xy(
            df.Longitude, df.Latitude, z=df.Altitude
        ),
        crs="EPSG:4326"
    )

    return gdf
