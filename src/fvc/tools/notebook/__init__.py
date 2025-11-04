import os
from pathlib import Path

import geopandas

from fvc.tools.df.utils import FvcDataset
from fvc.tools.utils import plnested


def fetch_geodata(file_name: str) -> geopandas.GeoDataFrame:
    input = Path(os.getenv('FVC_CACHE'), file_name)

    dataset = FvcDataset.read(input)
    metadata = dataset.metadata
    assert metadata and metadata['content'] == 'flightlog'

    df = dataset.df

    df = df.select(
        plnested('time.unix').alias('time'),
        plnested('pos.loc.lat').alias('lat'),
        plnested('pos.loc.lon').alias('lon'),
        plnested('pos.loc.alt').alias('alt'),
    )

    gdf = geopandas.GeoDataFrame(  # type: ignore
        df,
        geometry=geopandas.points_from_xy(
            df['lon'], df['lat'], z=df['alt']
        ),
        crs='EPSG:4326',
    )

    return gdf
