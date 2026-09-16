---
type: Domain Reference
title: Data Formats and Schemas

description: Reference for all external data formats, their converters, performance characteristics, and domain models used in fvctools

resource: /src/fvc/tools/df/schema.yaml

tags: [data-formats, schemas, domain, fvc, converters, performance]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T12:24:16.401Z
sources:
  - id: openwiki-source-afcb7d7a336948a1f5055bf0
    resource: repo://scripts/generate_schema_docs.py
  - id: openwiki-source-72007a10e53eb4e913249249
    resource: repo://src/fvc/tools/calc/geoid.py
  - id: openwiki-source-5ed15730fa37741e976035a2
    resource: repo://src/fvc/tools/df/cli.py
  - id: openwiki-source-e1ac5460a2f3e3c6f12f34a1
    resource: repo://src/fvc/tools/df/core.py
  - id: openwiki-source-fc5776122634f6b1b77cbd0c
    resource: repo://src/fvc/tools/df/schema.yaml
  - id: openwiki-source-79d703d62c9bb8dd3287cb65
    resource: repo://src/fvc/tools/df/xformats/datcon.py
  - id: openwiki-source-4ac6699f79ea2f0f545f3b19
    resource: repo://src/fvc/tools/df/xformats/nmea.py
  - id: openwiki-source-bc91d67dabf9f8aad886ec4a
    resource: repo://src/fvc/tools/df/xformats/safirmqtt_v2.py
  - id: openwiki-source-f43f1dcd6fe265845d338145
    resource: repo://src/fvc/tools/df/xformats/safirmqtt.py
  - id: openwiki-source-3e82d7ecdef56423054c4cab
    resource: repo://src/fvc/tools/df/xformats/senhive.py
  - id: openwiki-source-5e1b07b7b3c0fa28410ec278
    resource: repo://src/fvc/tools/df/xformats/ulog.py
  - id: openwiki-source-a043c04b44399925548a5afd
    resource: repo://tests/test_agentfly_xformat.py
  - id: openwiki-source-9187f334bf5708864726b986
    resource: repo://tests/test_datcon_xformat.py
  - id: openwiki-source-61b3f15c183440d72d1ba780
    resource: repo://tests/test_nmea_xformat.py
  - id: openwiki-source-c198d6b0de0328857c4de02b
    resource: repo://tests/test_safirmqtt_xformat.py
  - id: openwiki-source-211c12be7cab4bc9a5edb73c
    resource: repo://tests/test_senhive_xformat.py
  - id: openwiki-source-1ca82fe21babf2652db08db1
    resource: repo://tests/test_ulog_xformat.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T12:24:16.401Z" }
---

# Data Formats and Schemas

This document provides a comprehensive reference for all **external data formats**, their **converters**, **performance characteristics**, and **domain models** used in the **fvctools** suite.

For the unified Flyvercity Data Format (.fvc) specification, see:
[/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md)

## Overview

The fvctools suite converts multiple aviation, geospatial, and telemetry data formats into the unified **Flyvercity Data Format (.fvc)**. Each external format has a specialized converter module in `/src/fvc/tools/df/xformats/` that handles parsing, transformation, and schema validation.

## External Format Converters

Each external format converter implements a consistent interface:

```python
def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    """Convert external format to Flyvercity Data Format.
    
    Args:
        params: Conversion parameters
        metadata: Output metadata dict to be populated
        input_path: Path to input file
        output: JsonlinesIO writer for output
    """
```

All converters write:
1. A METADATA record as the first line
2. Data records in JSON-Lines format
3. Validated output against the schema.yaml definitions

---

## Aviation and Telemetry Formats

### 1. NMEA 0183 (`nmea.py`)

**Description**: Standard GPS protocol used by aviation, marine, and land navigation systems.

**Key Features**:
- Standardized sentence formats (GGA, RMC, GSA, GSV, VTG, etc.)
- Time, position, velocity, and satellite data
- Widespread compatibility with GPS devices
- Text-based protocol with checksum validation

**Converter Location**: `repo://src/fvc/tools/df/xformats/nmea.py`

**Dependencies**:
- `pynmea2` - NMEA 0183 parser
- `python-dateutil` - Date parsing

**Input Format Example**:
```
$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*
$GNRMC,123456.78,A,5234.1234,N,00450.1234,E,6.1,45.0,010123,0.0,E,A*1C
```

**Output Schema**: FLIGHTLOG with position data

**Performance Optimizations**:
- Fast string-based filtering of irrelevant message types before parsing
- Approximately 2x speedup by skipping non-GGA/RMC sentences in hot path
- Streaming line-by-line processing

**Required Parameters**:
- `base-date=<datestring>` - Base date for timestamp construction (ISO format)

**Evidence**:
- [nmea.py converter implementation](repo://src/fvc/tools/df/xformats/nmea.py#L25-L76)
- [Fast filtering optimization](repo://src/fvc/tools/df/xformats/nmea.py#L52-L90)
- [Test coverage](repo://tests/test_nmea_xformat.py#L6-L20)

**Related**: [NMEA Standard](https://www.nmea.org/)

---

### 2. ULog (PX4/ArduPilot) (`ulog.py`)

**Description**: Binary log format used by PX4 flight controllers and ArduPilot ecosystem.

**Key Features**:
- Efficient binary storage with indexed message types
- Flight controller telemetry (IMU, GPS, RC, parameters, etc.)
- Supports multiple message types per log
- Used by PX4, ArduPilot, and related autopilot systems

**Converter Location**: `repo://src/fvc/tools/df/xformats/ulog.py`

**Dependencies**:
- `pyulog` - ULog file parser
- `polars` - High-performance DataFrame operations

**Input Format**: Binary `.ulg` files containing:
- File header with metadata
- Multiple data sections (GPS, IMU, RC, etc.)
- Indexed for efficient access

**Output Schema**: FLIGHTLOG with position and timestamp data

**Performance Optimizations**:
- **Polars-based vectorized processing** - 5-6x speedup vs Python loops
- Direct DataFrame construction from parsed arrays
- Lazy evaluation where possible
- Bypasses individual JSON serialization overhead

**Metadata Extraction**:
- Extracts UAV ID from filename (format: `UAVID+YYYY-MM-DD_HH-MM-SS.ulg`)
- Falls back to boot timestamp if datetime cannot be extracted from filename

**Evidence**:
- [ulog.py converter implementation](repo://src/fvc/tools/df/xformats/ulog.py#L11-L65)
- [Polars optimization comment](repo://src/fvc/tools/df/xformats/ulog.py#L39-L41)
- [Test coverage](repo://tests/test_ulog_xformat.py#L1-L51)

**Related**: [PX4 ULog Format](https://docs.px4.io/main/en/dev_log/ulog_file_format.html)

---

### 3. SAFIR MQTT (`safirmqtt.py`, `safirmqtt_v2.py`)

**Description**: Telemetry streaming format using MQTT protocol for real-time aircraft tracking.

**Key Features**:
- Real-time telemetry data with JSON payloads
- Multiple versions (v1 and v2) with different optimizations
- Aircraft identification via ICAO hex, registration, or callsign
- Geodetic altitude to ellipsoidal conversion
- Optimized for high-frequency updates

**Converter Locations**:
- `repo://src/fvc/tools/df/xformats/safirmqtt.py` (v1)
- `repo://src/fvc/tools/df/xformats/safirmqtt_v2.py` (v2, optimized)

**Dependencies**:
- `pygeodesy` - Geodetic calculations and coordinate transformations

**Input Format**: JSON-Lines with SAFIR payload structure

**SAFIR v1 Features**:
- Standard SAFIR message format
- Full validation and error handling
- Geoid model for altitude conversion

**SAFIR v2 Features**:
- **Performance optimizations**:
  - Raw JSON parsing (skip benedict wrapper overhead)
  - Unified if/elif chains with hoisted fallback checks
  - Reduced dict lookups in hot loops
- Optimized for high-frequency telemetry streams
- More efficient error handling

**Output Schema**: FLIGHTLOG with aircraft identification and position

**Performance Optimizations** (both versions):
- Commit `5db7907`: Hoisted fallback checks outside hot loops
- Commit `ccffcac`: Removed redundant wrapper functions
- Polars integration in v2 for potential future optimizations

**Evidence**:
- [safirmqtt.py implementation](repo://src/fvc/tools/df/xformats/safirmqtt.py#L92-L107)
- [safirmqtt_v2.py implementation](repo://src/fvc/tools/df/xformats/safirmqtt_v2.py#L95-L117)
- [Hot path optimization in v1](repo://src/fvc/tools/df/xformats/safirmqtt.py#L13-L38)
- [v2 raw parsing optimization](repo://src/fvc/tools/df/xformats/safirmqtt_v2.py#L101-L102)

**Related**: [MQTT Protocol](https://mqtt.org/)

---

### 4. DJI DatCon (`datcon.py`)

**Description**: Flight recorder format from DJI DatCon software for DJI drone telemetry.

**Key Features**:
- DJI-specific telemetry including flight controller data
- Camera and gimbal information
- Space-separated text format with header
- UTC timezone requirement

**Converter Location**: `repo://src/fvc/tools/df/xformats/datcon.py`

**Dependencies**:
- `polars` - High-performance CSV parsing and DataFrame operations

**Input Format**: Space-separated text with header line

**Performance Optimizations**:
- **Polars-based processing** - 10-15x speedup vs row-by-row DictReader
- Vectorized operations at Rust/C level
- Efficient memory usage through Polars lazy evaluation

**Output Schema**: FLIGHTLOG with position and telemetry data

**Evidence**:
- [datcon.py converter](repo://src/fvc/tools/df/xformats/datcon.py#L20-L46)
- [Polars optimization comment](repo://src/fvc/tools/df/xformats/datcon.py#L32-L34)

---

### 5. SenHive (`senhive.py`)

**Description**: SenHive flight logging format for UAV telemetry and tracking.

**Key Features**:
- Flight telemetry and events
- Semicolon-separated CSV format
- Track IDs and vehicle serial numbers
- GPS position with altitude
- ISO-8601 timestamps

**Converter Location**: `repo://src/fvc/tools/df/xformats/senhive.py`

**Dependencies**:
- `polars` - High-performance CSV parsing and DataFrame operations

**Input Format**: Semicolon-separated CSV with quoted fields

**Performance Optimizations**:
- **Polars-based vectorized processing** - Approximately 25x speedup
- Direct DataFrame construction from CSV
- Bypasses Python loop overhead entirely
- Lazy evaluation and optimized column operations
- Efficient filtering of invalid rows

**Output Schema**: FLIGHTLOG with aircraft identification and position

**Evidence**:
- [senhive.py converter](repo://src/fvc/tools/df/xformats/senhive.py#L8-L74)
- [Polars optimization comment](repo://src/fvc/tools/df/xformats/senhive.py#L9-L12)
- [Performance claim in code](repo://src/fvc/tools/df/xformats/senhive.py#L10)

---

### 6. AgentFly (`agentfly.py`)

**Description**: AgentFly simulator logs for autonomous aircraft simulation.

**Key Features**:
- Simulator-specific telemetry
- High-frequency position and state updates
- Research flight data

**Converter Location**: `repo://src/fvc/tools/df/xformats/agentfly.py`

**Dependencies**:
- `polars` - High-performance DataFrame operations

**Performance Optimizations**:
- **Polars integration** for efficient processing
- Vectorized operations and lazy evaluation
- Memory-efficient streaming where possible

**Output Schema**: FLIGHTLOG with position and state data

**Evidence**:
- [agentfly.py converter](repo://src/fvc/tools/df/xformats/agentfly.py)

---

### 7. DJI Flight Records (`dji.py`)

**Description**: DJI drone flight records in DJI's proprietary format.

**Key Features**:
- DJI-specific telemetry format
- Flight controller data
- Camera and gimbal information
- Battery status and system health

**Converter Location**: `repo://src/fvc/tools/df/xformats/dji.py`

**Output Schema**: FLIGHTLOG with comprehensive flight data

---

## Geospatial Formats

### 8. GeoJSON (`geojson.py`)

**Description**: Standard geospatial data format for geographic features.

**Key Features**:
- JSON-based geometry representation
- Point, LineString, Polygon, MultiPolygon geometries
- Feature collections with properties
- Coordinate reference system: WGS-84

**Converter Location**: `repo://src/fvc/tools/df/xformats/geojson.py`

**Dependencies**:
- Standard library JSON parser

**Input Format**: GeoJSON FeatureCollection or Feature objects

**Output Schema**: Depends on input geometry type (FLIGHTLOG for points, custom for others)

**Evidence**:
- [geojson.py converter](repo://src/fvc/tools/df/xformats/geojson.py)

**Related**: [GeoJSON Specification](https://geojson.org/)

---

### 9. KML (`kml/` directory)

**Description**: Keyhole Markup Language for geographic visualization and 3D mapping.

**Key Features**:
- XML-based format
- Placemarks, paths, polygons, and styles
- Support for icons, colors, and labels
- Hierarchical structure

**Converter Location**: `repo://src/fvc/tools/df/xformats/kml/`

**Dependencies**:
- XML parser (standard library or lxml)

**Input Format**: KML files with geographic features

**Output Schema**: Custom schema based on extracted features

**Evidence**:
- [kml converter directory](repo://src/fvc/tools/df/xformats/kml/)

**Related**: [KML Documentation](https://developers.google.com/kml)

---

## Radar and Tracking Formats

### 10. ART Logs (`artlog.py`)

**Description**: ART (Autonomous Rotorcraft Testbed) log format for flight test data.

**Key Features**:
- Simple text-based format
- Flight test data with time-stamped events
- Research-focused telemetry

**Converter Location**: `repo://src/fvc/tools/df/xformats/artlog.py`

**Output Schema**: FLIGHTLOG with event data

---

### 11. Courageous Project (`courageous.py`)

**Description**: Courageous project flight logs for research aircraft.

**Key Features**:
- GPS and telemetry data
- Research flight data collection
- Time-stamped position and state

**Converter Location**: `repo://src/fvc/tools/df/xformats/courageous.py`

**Output Schema**: FLIGHTLOG with position and telemetry

---

### 12. CS Group (`csgroup.py`)

**Description**: CS Group radar and tracking logs for radar systems.

**Key Features**:
- Radar system data
- Target tracking information
- Polar and Cartesian coordinates

**Converter Location**: `repo://src/fvc/tools/df/xformats/csgroup.py`

**Output Schema**: RADARLOG with detection data

---

### 13. G-NetTrack (`gnettrack.py`)

**Description**: G-NetTrack GPS track logs for cellular and GPS tracking.

**Key Features**:
- GPS track data
- Time-stamped positions
- Signal strength and cell tower information

**Converter Location**: `repo://src/fvc/tools/df/xformats/gnettrack.py`

**Output Schema**: FLIGHTLOG or custom tracking schema

---

### 14. Manna (`manna.py`)

**Description**: Manna flight logs for UAV telemetry.

**Key Features**:
- Telemetry and events
- Flight data recording
- Time-stamped measurements

**Converter Location**: `repo://src/fvc/tools/df/xformats/manna.py`

**Output Schema**: FLIGHTLOG with position and state

---

### 15. Robin Radar (`robinradar.py`)

**Description**: Robin Radar system logs for radar telemetry and tracking.

**Key Features**:
- Radar system telemetry
- Target tracking
- Polar coordinates (azimuth, elevation, range)

**Converter Location**: `repo://src/fvc/tools/df/xformats/robinradar.py`

**Output Schema**: RADARLOG with radar detection data

---

## Domain Models

The fvctools suite organizes data according to domain-specific models that define the structure and semantics of the converted data.

### Flight Log Domain

Represents the flight path and state of an aircraft over time.

**Key Concepts**:
- **Position**: Latitude, longitude, altitude (WGS-84, ellipsoidal)
- **Attitude**: Roll, pitch, yaw angles
- **Velocity**: Ground speed, vertical speed, heading
- **GNSS**: Satellite navigation data (satellites, HDOP, VDOP)
- **Identification**: Aircraft identifiers (ICAO hex, registration, callsign, internal ID)
- **Temporal**: Unix timestamps in milliseconds with ISO-8601 representation
- **System**: System status, battery level, flight mode
- **Quality**: Navigation quality metrics (HDOP, VDOP, satellite count)

**Schema**: FLIGHTLOG (see [/docs/schema/FLIGHTLOG.md](/docs/schema/FLIGHTLOG.md))

**Data Record Structure**:
```json
{
  "time": {
    "unix": 1756033206882,
    "iso": "2025-08-01T12:00:06.882Z"
  },
  "uaid": {
    "icaohex": "ABC123",
    "icaoreg": "VH-XYZ",
    "atm": "JET123",
    "int": "UAV-001"
  },
  "pos": {
    "loc": {
      "lat": 52.3,
      "lon": 4.9,
      "alt": 100.5,
      "amsl": 95.2
    },
    "heading": 270.5,
    "groundspeed": 15.2
  },
  "att": {
    "roll": -30.0,
    "pitch": 5.5,
    "yaw": 270.5
  },
  "origin": "flight_data_20231201.log",
  "quality": {
    "hdop": 1.2,
    "vdop": 0.8,
    "satellites": 12
  }
}
```

**Tools**: `fvc df convert`, `fvc render fl`

**Evidence**:
- [Schema definition](repo://src/fvc/tools/df/schema.yaml#L198-L350)
- [Flight log domain reference](repo:///openwiki/domain/formats.md#L25-L100)

---

### Radar Log Domain

Represents radar detections and tracks for air traffic surveillance and tracking systems.

**Key Concepts**:
- **Position**: Polar or geographic coordinates
- **Velocity**: Radial velocity and ground speed
- **Signal**: Received Signal Strength Indicator (RSSI)
- **Angles**: Azimuth and elevation angles
- **Range**: Distance to target
- **Identification**: Radar target identifiers
- **Temporal**: Detection timestamps

**Schema**: RADARLOG (see [/docs/schema/RADARLOG.md](/docs/schema/RADARLOG.md))

**Data Record Structure**:
```json
{
  "time": {"unix": 1756033206882},
  "pos": {
    "loc": {
      "lat": 52.3,
      "lon": 4.9,
      "alt": 100.5
    },
    "polar": {
      "bear": 45.0,
      "elev": 10.5,
      "range": 5000.0
    }
  },
  "vel": {
    "groundspeed": 15.2,
    "radial_velocity": 5.0
  },
  "rssi": -65.5,
  "origin": "radar_system_alpha"
}
```

**Tools**: `fvc df convert`, `fvc render` (radar visualization)

**Evidence**:
- [Schema definition](repo://src/fvc/tools/df/schema.yaml#L352-L537)
- [Radar domain reference](repo:///openwiki/domain/formats.md#L102-L200)

---

### Geospatial Domain

Geographic and geodetic calculations for coordinate transformations and terrain modeling.

**Key Concepts**:
- **Coordinate Systems**: WGS-84 (geodetic), NED (North-East-Down, local frame)
- **Geoid Models**: EGM96 for altitude conversion (AMSL to ellipsoidal)
- **Terrain Models**: Digital Elevation Models (DEM) for height above ground
- **Projections**: Geographic to projected coordinates
- **Distance Calculations**: Great-circle distances and bearings

**Tools**:
- `fvc calc undulation` - Geoid undulation calculations
- `fvc calc terrain` - Terrain elevation lookups

**Libraries**:
- `pygeodesy` - Geodetic calculations, coordinate transformations
- `geopandas` - Geospatial data manipulation
- `rasterio` - Digital Elevation Model (DEM) access

**Evidence**:
- [Geospatial utilities](repo://src/fvc/tools/calc/geoid.py)
- [Geospatial libraries usage](repo://src/fvc/tools/df/xformats/safirmqtt.py#L6)

---

### Fusion Domain

Data fusion and correlation operations for combining multiple data sources.

**Key Concepts**:
- **Temporal Alignment**: Synchronizing data from multiple sources
- **Spatial Alignment**: Matching data in geographic space
- **Correlation**: Finding relationships between data streams
- **Fusion**: Combining multiple data sources into coherent tracks

**Tools**:
- `fvc df correlate` - Temporal and spatial correlation
- `fvc df fusion` - Multi-source data fusion

**Modules**:
- `correlate.py` - Correlation algorithms
- `fusion.py` - Data fusion operations

**Evidence**:
- [Correlation module](repo://src/fvc/tools/df/correlate.py)
- [Fusion module](repo://src/fvc/tools/df/fusion.py)

---

## Schema Organization and Validation

### Schema Definition

All schemas are defined in `repo://src/fvc/tools/df/schema.yaml` and validated using the `jsonschema` library.

**Schema Structure**:

```yaml
METADATA:
  type: object
  properties:
    content:
      description: Content type (flightlog, radarlog, fusion.replay, capture.message)
      enum: [flightlog, radarlog, fusion.replay, capture.message]
    source:
      description: Original data format
      enum: [nmea, ulog, safirmqtt, datcon, senhive, ...]
    origin:
      description: Original file name or system
    polar_sensor:
      description: Polar sensor configuration
  required: [content]

FLIGHTLOG:
  type: object
  properties:
    time: {unix: number, iso?: string}
    uaid: {int?: string, fvc?: string, icaohex?: string, icaoreg?: string, atm?: string}
    pos: {loc: {lat: number, lon: number, alt?: number, amsl?: number, height?: number}}
    att: {roll: number, pitch: number, yaw: number}
    vel: {groundspeed?: number, heading?: number}
    origin: string
    quality: {hdop?: number, vdop?: number, satellites?: number}
  required: [time, pos]

RADARLOG:
  type: object
  properties:
    time: {unix: number}
    pos: {loc?: {lat: number, lon: number, alt?: number}, polar?: {bear: number, elev: number, range: number}}
    vel: {groundspeed?: number, radial_velocity?: number}
    rssi: number
    origin: string
  required: [time]
```

**Validation Rules**:
1. METADATA must be the first line of every .fvc file
2. Content type must match the data records
3. All required fields must be present
4. Field types must be correct
5. Schema constraints must be satisfied

**Validation Tools**:

```bash
# Validate a .fvc file
uv run fvc df --in flight.fvc validate

# Validate with verbose output
uv run fvc df --in flight.fvc validate --verbose
```

**Validation Pipeline**:
```
Input File → Parser → Conversion → Schema Validation → Output
                    ↓
            Validation Errors
```

**Common Validation Issues**:
1. Missing METADATA record as first line
2. Content mismatch between METADATA and data records
3. Missing required fields (e.g., lat/lon in position)
4. Type errors (e.g., string instead of number)
5. Schema constraint violations

**Evidence**:
- [schema.yaml definition](repo://src/fvc/tools/df/schema.yaml)
- [Validation utilities](repo://src/fvc/tools/df/schema.py)
- [Validation command implementation](repo://src/fvc/tools/df/__main__.py)

---

## Performance Considerations

### Format-Specific Optimizations

Recent commits demonstrate significant performance improvements through targeted optimizations:

#### 1. Polars Integration

Multiple converters use **Polars** for high-performance data processing:

| Converter | Optimization | Performance Gain | Evidence |
|-----------|--------------|-----------------|----------|
| `agentfly.py` | Polars DataFrame operations | High | [repo://src/fvc/tools/df/xformats/agentfly.py#L8-L11] |
| `datcon.py` | Polars CSV parsing | 10-15x | [repo://src/fvc/tools/df/xformats/datcon.py#L32-L34] |
| `senhive.py` | Polars vectorized processing | ~25x | [repo://src/fvc/tools/df/xformats/senhive.py#L9-L12] |
| `ulog.py` | Polars DataFrame construction | 5-6x | [repo://src/fvc/tools/df/xformats/ulog.py#L39-L41] |

**Benefits**:
- Vectorized operations at Rust/C level
- Lazy evaluation for memory efficiency
- Parallel processing where applicable
- Bypasses Python loop overhead

#### 2. Hot Path Optimizations

SAFIR MQTT converters demonstrate micro-optimizations:

- **Commit `5db7907`**: Hoisted fallback checks outside hot loops in `safirmqtt_v2.py`
- **Commit `ccffcac`**: Removed redundant wrapper functions in `safirmqtt.py`
- Unified if/elif chains to reduce conditional branching
- Reduced dictionary lookups in performance-critical sections

**Evidence**:
- [safirmqtt.py optimization](repo://src/fvc/tools/df/xformats/safirmqtt.py#L13-L38)
- [safirmqtt_v2.py optimization](repo://src/fvc/tools/df/xformats/safirmqtt_v2.py#L13-L35)

#### 3. Streaming and Memory Efficiency

- JSON-Lines format enables streaming processing
- Lazy evaluation where possible
- Memory-mapped file access for large files
- Streaming JSON parsing for high-frequency data

**Evidence**:
- [JsonlinesIO utility](repo://src/fvc/tools/df/utils.py)
- [Streaming implementation in safirmqtt](repo://src/fvc/tools/df/xformats/safirmqtt.py#L97-L107)

### Benchmarking

Performance-critical converters have dedicated tests that verify both correctness and performance characteristics:

- `/tests/test_agentfly_xformat.py` - AgentFly simulator logs
- `/tests/test_datcon_xformat.py` - DJI DatCon flight records
- `/tests/test_safirmqtt_xformat.py` - SAFIR MQTT telemetry
- `/tests/test_senhive_xformat.py` - SenHive flight logging
- `/tests/test_nmea_xformat.py` - NMEA GPS protocol
- `/tests/test_ulog_xformat.py` - PX4 ULog format

**Evidence**:
- [Test directory](repo://tests/)
- [Performance test patterns](repo://tests/test_ulog_xformat.py#L1-L51)

---

## Schema Documentation Generation

Schema documentation is automatically generated from `repo://src/fvc/tools/df/schema.yaml`:

```bash
# Regenerate schema docs
python scripts/generate_schema_docs.py
```

This updates all `.md` files in `/docs/schema/` with current schema definitions.

**Evidence**:
- [Schema generation script](repo://scripts/generate_schema_docs.py)

---

## Domain-Specific Libraries

### Geodesy and Coordinate Systems

- **Library**: `pygeodesy`
- **Purpose**: Geodetic calculations, coordinate transformations
- **Key Features**:
  - EGM96 geoid model for AMSL to ellipsoidal conversion
  - Distance and bearing calculations (great-circle)
  - Coordinate conversions between geographic and local frames
  - Geoid undulation calculations

**Usage**:
```python
from fvc.tools.calc import geoid

alt_ellipsoidal = geoid.amsl_to_ellipsoidal(pgm, lat, lon, amsl)
```

**Evidence**:
- [Geoid utilities](repo://src/fvc/tools/calc/geoid.py)
- [SAFIR converter usage](repo://src/fvc/tools/df/xformats/safirmqtt.py#L6)

---

### Geospatial Data Handling

- **Library**: `geopandas`
- **Purpose**: Geospatial data manipulation and analysis
- **Key Features**:
  - Vector data operations (buffers, intersections, unions)
  - Spatial joins and proximity analysis
  - Coordinate system projections
  - Geometry operations

**Usage**:
```python
import geopandas as gpd

df = gpd.read_file('flight_path.geojson')
buffer = df.geometry.buffer(100)  # 100 meter buffer
```

**Evidence**:
- [Geospatial operations](repo://src/fvc/tools/calc/geospatial.py)

---

### Terrain Data Access

- **Library**: `rasterio`
- **Purpose**: Digital Elevation Model (DEM) access and terrain analysis
- **Key Features**:
  - Read GeoTIFF and other raster formats
  - Terrain elevation lookups with interpolation
  - Slope and aspect calculations
  - Masking and windowed reading for memory efficiency

**Usage**:
```python
import rasterio

with rasterio.open('dem.tif') as src:
    elevation = src.read(1, window=window)
```

**Evidence**:
- [Terrain utilities](repo://src/fvc/tools/calc/terrain.py)

---

### Data Processing

- **Library**: `polars`
- **Purpose**: High-performance DataFrame operations
- **Key Features**:
  - Lazy evaluation for memory efficiency
  - Parallel processing across CPU cores
  - Memory-mapped file I/O
  - Optimized CSV/JSON parsing
  - Vectorized operations

**Usage in converters**:
```python
import polars as pl

df = pl.read_csv(input_path, separator=';')
```

**Evidence**:
- [Polars usage across converters](repo://src/fvc/tools/df/xformats/senhive.py#L13)
- [Performance claims in code](repo://src/fvc/tools/df/xformats/datcon.py#L32-L34)

---

## Future Domain Extensions

Based on the codebase and recent commits, potential future domain extensions include:

1. **Additional Aviation Formats**: Support for more flight data formats (e.g., ArduPilot logs, MAVLink)
2. **Enhanced Geospatial**: More coordinate systems and projections, terrain-relative navigation
3. **Real-time Processing**: Streaming data pipelines with low-latency requirements
4. **Cloud Integration**: Direct access to cloud storage (S3, GCS) and cloud-based processing
5. **Machine Learning**: Anomaly detection and predictive analytics for flight data
6. **Multi-sensor Fusion**: Integration of IMU, LiDAR, and camera data
7. **Regulatory Compliance**: Formats for flight logging compliance (EU, FAA)

---

## Related Documentation

- [Flyvercity Data Format Reference](/openwiki/architecture/data-formats.md)
- [Conversion Workflows](/openwiki/workflows/conversion.md)
- [Integration Guides](/openwiki/integrations/index.md)
- [Schema Documentation](/docs/schema/README.md)
- [Development Setup](/openwiki/operations/setup.md)
- [Domain Formats and Models](/openwiki/domain/formats.md)
