from pathlib import Path
import yaml
from typing import Dict, Any


def load_schema() -> Dict[str, Any]:
    schema_path = Path(__file__).parent / 'schema.yaml'

    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


# Load the schema
SCHEMA = load_schema()

# Export individual schemas for backward compatibility
LOCATION = SCHEMA['LOCATION']
POLAR = SCHEMA['POLAR']
POLAR_SENSOR = SCHEMA['POLAR_SENSOR']
IDENTIFICATION = SCHEMA['IDENTIFICATION']
CONTENT = SCHEMA['CONTENT']
METADATA = SCHEMA['METADATA']
ATTITUDE = SCHEMA['ATTITUDE']
POSITION = SCHEMA['POSITION']
RADAR_POSITION = SCHEMA['RADAR_POSITION']
TIMESTAMP = SCHEMA['TIMESTAMP']
CELLULAR_SIGNAL = SCHEMA['CELLULAR_SIGNAL']
FLIGHTLOG = SCHEMA['FLIGHTLOG']
RADARLOG = SCHEMA['RADARLOG']
FUSION_REPLAY = SCHEMA['FUSION_REPLAY']
CONTENT_SCHEMA = SCHEMA['CONTENT_SCHEMA']
