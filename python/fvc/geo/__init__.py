import pandas
import geopandas

from fvc.df.util import fetch_input_file, JsonlinesIO


def fetch_geodata(file_name: str) -> gpd.GeoDataFrame:
    file_path = fetch_input_file(input_filename=file_name)

    with JsonlinesIO(file_path, 'r') as io:
        metadata = io.read()
        assert metadata['content'] == 'flightlog'

        def fetch(record):
            return (
                record['pos']['loc']['lat'],
                record['pos']['loc']['lon']
            )

        data = list(zip(*map(fetch, io.iterate())))

    df = pandas.DataFrame({
        'Latitude': data[0],
        'Longitude': data[1]
    })

    gdf = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.Longitude, df.Latitude),
        crs="EPSG:4326"
    )

    return gdf
