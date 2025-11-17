import os
import logging as lg
from pathlib import Path

from pygeodesy.geoids import GeoidPGM


def load_geoid(params={}, metadata=None) -> GeoidPGM:
    pgm_path = Path(os.getenv('FVC_CACHE')) / 'geo' / 'egm96-5' / 'egm96-5.pgm'

    if egm := params.get('EGM'):
        pgm_path = Path(egm)

    lg.debug(f'Using geoid model: {pgm_path.absolute()}')

    if metadata:
        metadata.update({'geoid': pgm_path.name})

    geoid = GeoidPGM(pgm_path)
    return geoid


def amsl_to_ellipsoidal(
    geoid: GeoidPGM, lat: float, lon: float, amsl_height: float
) -> float:
    # Initialize the Geoid model using EGM96 with WGS-84 datum
    geoid_height = geoid.height(lat, lon)
    ellipsoidal_height = amsl_height + geoid_height  # type: ignore
    return ellipsoidal_height


def ellipsoid_to_amsl(
    geoid: GeoidPGM, lat: float, lon: float, ellipsoid_height: float
) -> float:
    geoid_height = geoid.height(lat, lon)
    lg.debug(f'Geoid height: {geoid_height}')
    amsl_height = ellipsoid_height - geoid_height  # type: ignore
    return amsl_height
