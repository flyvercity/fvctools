---
type: Domain Reference
title: Data Formats and Schemas

description: Reference for all data formats, schemas, and domain models used in fvctools
resource: /src/fvc/tools/df/schema.yaml

tags: [data-formats, schemas, domain, fvc]
---

# Data Formats and Schemas

This document provides a comprehensive reference for all data formats, schemas, and domain models used in the **fvctools** suite.

## Overview

The fvctools suite works with multiple data formats across different aviation and geospatial domains. This document organizes and explains each format and its schema.

## Core Data Format: Flyvercity (.fvc)

See [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md) for complete documentation of the Flyvercity Data Format.

## External Format Converters

Each external format has a specialized converter module in `/src/fvc/tools/df/xformats/`. Below are the key formats and their characteristics.

### 1. NMEA 0183 (`nmea.py`)

**Description**: Standard GPS protocol used by most aviation and marine navigation systems.

**Key Features**:
- Standardized sentence formats (GGA, RMC, GSA, GSV, etc.)
- Time, position, velocity, and satellite data
- Widespread compatibility with GPS devices

**Converter Location**: `/src/fvc/tools/df/xformats/nmea.py`

**Example NMEA Sentences**:
```
$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*
$GNRMC,123456.78,A,5234.1234,N,00450.1234,E,6.1,45.0,010123,0.0,E,A*1C
```

**Related**: [NMEA Standard](https://www.nmea.org/)

### 2. ULog (PX4) (`ulog.py`)

**Description**: Binary log format used by PX4 flight controllers.

**Key Features**:
- Binary format with efficient storage
- Flight controller telemetry and parameters
- Supports multiple message types
- Used by ArduPilot and PX4 ecosystems

**Converter Location**: `/src/fvc/tools/df/xformats/ulog.py`

**Dependencies**: `pyulog` library

**Related**: [PX4 ULog Format](https://docs.px4.io/main/en/dev_log/ulog_file_format.html)

### 3. SAFIR MQTT (`safirmqtt.py`, `safirmqtt_v2.py`)

**Description**: Telemetry streaming format using MQTT protocol.

**Key Features**:
- Real-time telemetry data
- JSON-based payloads
- Multiple versions (v1 and v2)
- Optimized for high-frequency updates

**Converter Locations**:
- `/src/fvc/tools/df/xformats/safirmqtt.py` (v1)
- `/src/fvc/tools/df/xformats/safirmqtt_v2.py` (v2, optimized)

**Recent Optimizations**:
- Commit `5db7907`: Hoisted fallback checks outside hot loops
- Commit `ccffcac`: Removed redundant wrapper functions
- Polars-based optimizations for v2

**Related**: [MQTT Protocol](https://mqtt.org/)

### 4. DatCon (`datcon.py`)

**Description**: Flight recorder format from DatCon software.

**Key Features**:
- Flight data recording
- Telemetry and event data
- Optimized with Polars (commit `b3858c6`)

**Converter Location**: `/src/fvc/tools/df/xformats/datcon.py`

**Performance**: Optimized with Polars for faster processing

### 5. SenHive (`senhive.py`)

**Description**: SenHive flight logging format.

**Key Features**:
- Flight telemetry and events
- Optimized with Polars (commit `a456910`)

**Converter Location**: `/src/fvc/tools/df/xformats/senhive.py`

**Performance**: Polars-based optimizations for efficient processing

### 6. AgentFly (`agentfly.py`)

**Description**: AgentFly simulator logs.

**Key Features**:
- Simulator-specific telemetry
- Optimized with Polars (commit `a456910`)

**Converter Location**: `/src/fvc/tools/df/xformats/agentfly.py`

**Performance**: Polars integration for high-performance conversion

### 7. DJI Flight Records (`dji.py`)

**Description**: DJI drone flight records.

**Key Features**:
- DJI-specific telemetry format
- Flight controller data
- Camera and gimbal information

**Converter Location**: `/src/fvc/tools/df/xformats/dji.py`

### 8. GeoJSON (`geojson.py`)

**Description**: Standard geospatial data format.

**Key Features**:
- JSON-based geometry representation
- Point, LineString, Polygon geometries
- Feature collections

**Converter Location**: `/src/fvc/tools/df/xformats/geojson.py`

**Related**: [GeoJSON Specification](https://geojson.org/)

### 9. KML (`kml/` directory)

**Description**: Keyhole Markup Language for geographic visualization.

**Key Features**:
- XML-based format
- Placemarks, paths, polygons
- Support for styles and icons

**Converter Location**: `/src/fvc/tools/df/xformats/kml/`

**Related**: [KML Documentation](https://developers.google.com/kml)

### 10. ART Logs (`artlog.py`)

**Description**: ART (Autonomous Rotorcraft Testbed) log format.

**Key Features**:
- Simple text-based format
- Flight test data
- Time-stamped events

**Converter Location**: `/src/fvc/tools/df/xformats/artlog.py`

### 11. Courageous Project (`courageous.py`)

**Description**: Courageous project flight logs.

**Key Features**:
- GPS and telemetry data
- Research flight data

**Converter Location**: `/src/fvc/tools/df/xformats/courageous.py`

### 12. CS Group (`csgroup.py`)

**Description**: CS Group radar and tracking logs.

**Key Features**:
- Radar system data
- Tracking information

**Converter Location**: `/src/fvc/tools/df/xformats/csgroup.py`

### 13. G-NetTrack (`gnettrack.py`)

**Description**: G-NetTrack GPS track logs.

**Key Features**:
- GPS track data
- Time-stamped positions

**Converter Location**: `/src/fvc/tools/df/xformats/gnettrack.py`

### 14. Manna (`manna.py`)

**Description**: Manna flight logs.

**Key Features**:
- Telemetry and events
- Flight data recording

**Converter Location**: `/src/fvc/tools/df/xformats/manna.py`

### 15. Robin Radar (`robinradar.py`)

**Description**: Robin Radar system logs.

**Key Features**:
- Radar system telemetry
- Target tracking

**Converter Location**: `/src/fvc/tools/df/xformats/robinradar.py`

## Domain Models

### Flight Log Domain

Represents the flight path and state of an aircraft over time.

**Key Concepts**:
- **Position**: Latitude, longitude, altitude
- **Attitude**: Roll, pitch, yaw angles
- **Velocity**: Velocity components (NED frame)
- **GNSS**: Satellite navigation data
- **Cellular**: Cellular signal information
- **System**: System status and health

**Schema**: FLIGHTLOG (see [/docs/schema/FLIGHTLOG.md](/docs/schema/FLIGHTLOG.md))

**Tools**: `fvc df convert`, `fvc render fl`

### Radar Log Domain

Represents radar detections and tracks.

**Key Concepts**:
- **Position**: Polar or geographic coordinates
- **Velocity**: Radial velocity
- **Signal**: Received Signal Strength Indicator (RSSI)
- **Angles**: Azimuth and elevation
- **Range**: Distance to target

**Schema**: RADARLOG (see [/docs/schema/RADARLOG.md](/docs/schema/RADARLOG.md))

**Tools**: `fvc df convert`, `fvc render` (radar visualization)

### Geospatial Domain

Geographic and geodetic calculations.

**Key Concepts**:
- **Coordinate Systems**: WGS-84, NED (North-East-Down)
- **Geoid Models**: EGM96 for altitude conversion
- **Terrain Models**: Digital Elevation Models (DEM)
- **Projections**: Geographic to projected coordinates

**Tools**: `fvc calc undulation`, `fvc calc terrain`

**Libraries**: `pygeodesy`, `rasterio`

### Fusion Domain

Data fusion and correlation operations.

**Key Concepts**:
- **Temporal Alignment**: Synchronizing data from multiple sources
- **Spatial Alignment**: Matching data in geographic space
- **Correlation**: Finding relationships between data streams
- **Fusion**: Combining multiple data sources

**Tools**: `fvc df correlate`, `fvc df fusion`

**Modules**: `correlate.py`, `fusion.py`

## Schema Organization

All schemas are defined in `/src/fvc/tools/df/schema.yaml` and validated using the `jsonschema` library.

### Schema Structure

```yaml
METADATA:
  type: object
  properties:
    content:
      # Content type specification
    source:
      # Source format
    origin:
      # Origin identifier
    polar_sensor:
      # Optional polar sensor config

FLIGHTLOG:
  type: object
  properties:
    time:
      # Timestamp information
    pos:
      # Position information
    vel:
      # Velocity information
    att:
      # Attitude information
    # ... other flight log fields

RADARLOG:
  type: object
  properties:
    time:
      # Timestamp information
    pos:
      # Position (polar or geographic)
    vel:
      # Velocity information
    rssi:
      # Signal strength
    azimuth:
      # Azimuth angle
    elevation:
      # Elevation angle
    range:
      # Range/distance
```

### Schema Validation

All .fvc files are validated against the schema:

```python
from fvc.tools.df.schema import validate_fvc

validate_fvc(file_path)
```

**Validation Rules**:
- METADATA must be first line
- Content type must match data records
- All required fields must be present
- Field types must be correct
- Schema constraints must be satisfied

## Data Quality and Validation

### Validation Pipeline

```
Input File → Parser → Conversion → Schema Validation → Output
                    ↓
            Validation Errors
```

### Common Validation Issues

1. **Missing METADATA**: First line is not a valid METADATA record
2. **Content Mismatch**: Data record doesn't match METADATA content type
3. **Missing Fields**: Required fields are absent
4. **Type Errors**: Field has wrong data type
5. **Schema Violations**: Field value violates schema constraints

### Validation Tools

```bash
# Validate a .fvc file
uv run fvc df --in flight.fvc validate

# Validate with verbose output
uv run fvc df --in flight.fvc validate --verbose
```

## Performance Considerations

### Format-Specific Optimizations

Recent commits show significant performance improvements through:

1. **Polars Integration**:
   - `agentfly.py`: Polars-based optimizations (commit `a456910`)
   - `datcon.py`: Polars optimizations (commit `b3858c6`)
   - `senhive.py`: Polars optimizations (commit `a456910`)

2. **Hot Path Optimizations**:
   - `safirmqtt_v2.py`: Hoisted fallback checks (commit `5db7907`)
   - Unified if/elif chains for better performance
   - Removed redundant wrapper functions (commit `ccffcac`)

3. **Memory Efficiency**:
   - JSON-Lines format enables streaming
   - Polars DataFrames for efficient operations
   - Lazy evaluation where possible

### Benchmarking

Performance-critical converters have dedicated tests:

- `/tests/test_agentfly_xformat.py`
- `/tests/test_datcon_xformat.py`
- `/tests/test_safirmqtt_xformat.py`
- `/tests/test_senhive_xformat.py`

## Schema Documentation Generation

Schema documentation is automatically generated from `/src/fvc/tools/df/schema.yaml`:

```bash
# Regenerate schema docs
python scripts/generate_schema_docs.py
```

This updates all `.md` files in `/docs/schema/`.

## Domain-Specific Libraries

### Geodesy and Coordinate Systems

- **Library**: `pygeodesy`
- **Purpose**: Geodetic calculations, coordinate transformations
- **Key Features**:
  - EGM96 geoid model
  - Distance and bearing calculations
  - Coordinate conversions

### Geospatial Data Handling

- **Library**: `geopandas`
- **Purpose**: Geospatial data manipulation
- **Key Features**:
  - Vector data operations
  - Spatial joins
  - Projections

### Terrain Data Access

- **Library**: `rasterio`
- **Purpose**: Digital Elevation Model (DEM) access
- **Key Features**:
  - Read GeoTIFF and other raster formats
  - Terrain elevation lookups
  - Interpolation

### Data Processing

- **Library**: `polars`
- **Purpose**: High-performance DataFrame operations
- **Key Features**:
  - Lazy evaluation
  - Parallel processing
  - Memory efficiency

## Future Domain Extensions

Based on the codebase and recent commits, potential future domain extensions include:

1. **Additional Aviation Formats**: Support for more flight data formats
2. **Enhanced Geospatial**: More coordinate systems and projections
3. **Real-time Processing**: Streaming data pipelines
4. **Cloud Integration**: Direct access to cloud storage and APIs
5. **Machine Learning**: Anomaly detection and predictive analytics

## Related Documentation

- [Flyvercity Data Format Reference](/openwiki/architecture/data-formats.md)
- [Conversion Workflows](/openwiki/workflows/conversion.md)
- [Integration Guides](/openwiki/integrations/index.md)
- [Schema Documentation](/docs/schema/README.md)
- [Development Setup](/openwiki/operations/setup.md)
