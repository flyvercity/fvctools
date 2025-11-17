import os
from pathlib import Path
from typing import Optional

import math
import rasterio

from fvc.tools.calc.utils import lg


def height(
    lat_deg: float,
    lon_deg: float,
    amsl_height: float,
    copernicus_dir: Optional[str] = None,
) -> float:
    if not copernicus_dir:
        copernicus_dir = Path(os.getenv('FVC_CACHE')) / 'geo' / 'copernicus'

    tile_name = _copernicus_tile_name(lat_deg, lon_deg)
    tile_path = copernicus_dir / tile_name

    if not tile_path.exists():
        raise FileNotFoundError(f'Missing tile: {tile_name}')

    with rasterio.open(tile_path) as ds:
        # Convert lon/lat → raster row/col
        row, col = ds.index(lon_deg, lat_deg)
        value = ds.read(1)[row, col]

        # DEM nodata becomes None
        if value == ds.nodata:
            raise ValueError(f'No data at {lat_deg}, {lon_deg}')

        terrain = float(value)
        lg.debug(f'Terrain: {terrain}')
        agl = float(amsl_height - terrain)

    return agl


def _copernicus_tile_name(lat: float, lon: float) -> str:
    lat_floor = int(math.floor(lat))
    lon_floor = int(math.floor(lon))

    Hlat = 'N' if lat_floor >= 0 else 'S'
    Hlon = 'E' if lon_floor >= 0 else 'W'

    return f'Copernicus_DSM_COG_10_{Hlat}{abs(lat_floor):02d}_00_{Hlon}{abs(lon_floor):03d}_00_DEM.tif'
