import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

import math
import rasterio

from fvc.tools.calc.utils import lg


class Terrain:
    def __init__(
        self,
        copernicus_dir: Optional[str] = None,
        rough_cache: int | None = None,
    ):
        if not copernicus_dir:
            copernicus_dir = Path(os.getenv('FVC_CACHE')) / 'geo' / 'copernicus'

        self._copernicus_dir = copernicus_dir
        self._rough_cache = rough_cache
        self._dataset = {}
        self._cache = {}

    def __enter__(self):
        self._dataset = {}
        self._cache.clear()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for ds in self._dataset.values():
            ds.close()

        self._dataset.clear()

    def _get_dataset(self, lat_deg: float, lon_deg: float) -> rasterio.DatasetReader:
        if (lat_deg, lon_deg) in self._dataset:
            return self._dataset[(lat_deg, lon_deg)]

        tile_name = _copernicus_tile_name(lat_deg, lon_deg)
        tile_path = self._copernicus_dir / tile_name

        if not tile_path.exists():
            raise FileNotFoundError(f'Missing tile: {tile_name}')

        ds = rasterio.open(tile_path)
        self._dataset[(lat_deg, lon_deg)] = ds
        return ds

    def terrain(self, lat_deg: float, lon_deg: float) -> float:
        if self._rough_cache is not None:
            rough_lat = math.ceil(lat_deg * self._rough_cache)
            rough_lon = math.ceil(lon_deg * self._rough_cache)

            if (rough_lat, rough_lon) in self._cache:
                return self._cache[(rough_lat, rough_lon)]
            
        ds = self._get_dataset(lat_deg, lon_deg)
        row, col = ds.index(lon_deg, lat_deg)
        value = ds.read(1)[row, col]

        if value == ds.nodata:
            raise ValueError(f'No data at {lat_deg}, {lon_deg}')

        lg.debug(f'Terrain: {value} at {lat_deg}, {lon_deg}')

        if self._rough_cache is not None:
            self._cache[(rough_lat, rough_lon)] = value

        return float(value)

    def height(self, lat_deg: float, lon_deg: float, amsl_height: float) -> float:
        terrain = self.terrain(lat_deg, lon_deg)
        return float(amsl_height - terrain)


@lru_cache()
def _copernicus_tile_name(lat: float, lon: float) -> str:
    lat_floor = int(math.floor(lat))
    lon_floor = int(math.floor(lon))

    Hlat = 'N' if lat_floor >= 0 else 'S'
    Hlon = 'E' if lon_floor >= 0 else 'W'

    return f'Copernicus_DSM_COG_10_{Hlat}{abs(lat_floor):02d}_00_{Hlon}{abs(lon_floor):03d}_00_DEM.tif'
