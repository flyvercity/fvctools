import os
from pathlib import Path

import geopandas
import polars as pl

from fvc.tools.df.utils import FvcDataset


def fetch_geodata(file_name: str) -> geopandas.GeoDataFrame:
    input = Path(os.getenv('FVC_CACHE'), file_name)

    dataset = FvcDataset.read(input)
    metadata = dataset.metadata
    assert metadata and metadata['content'] == 'flightlog'

    df = dataset.df

    df = df.select(
        pl.col('time').struct.field('unix').alias('time'),
        pl.col('pos').struct.field('loc').struct.field('lat').alias('lat'),
        pl.col('pos').struct.field('loc').struct.field('lon').alias('lon'),
        pl.col('pos').struct.field('loc').struct.field('alt').alias('alt'),
    )

    print(df)

    gdf = geopandas.GeoDataFrame(  # type: ignore
        df,
        geometry=geopandas.points_from_xy(
            df['lon'], df['lat'], z=df['alt']
        ),
        crs='EPSG:4326',
    )

    return gdf
