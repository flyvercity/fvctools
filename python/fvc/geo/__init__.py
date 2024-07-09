import pandas
import geopandas
from itertools import tee

from fvc.df.util import fetch_input_file, JsonlinesIO


def fetch_geodata(file_name: str) -> geopandas.GeoDataFrame:
    file_path = fetch_input_file(input_filename=file_name)

    with JsonlinesIO(file_path, 'r') as io:
        metadata = io.read()
        assert metadata and metadata['content'] == 'flightlog'
        it = tee(io.iterate(), 2)

        df = pandas.DataFrame({
            'Latitude': list(map(lambda r: r['pos']['loc']['lat'], it[0])),
            'Longitude': list(map(lambda r: r['pos']['loc']['lon'], it[1]))
        })

    gdf = geopandas.GeoDataFrame(                    # type: ignore
        df,
        geometry=geopandas.points_from_xy(df.Longitude, df.Latitude),
        crs="EPSG:4326"
    )

    return gdf
