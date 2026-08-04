---
type: Data Formats Guide
title: Data Formats and Schemas

description: Comprehensive guide to Flyvercity Data Format (.fvc) and supported external formats
resource: /src/fvc/tools/df/schema.yaml

tags: [data-formats, schemas, fvc, json-lines, validation]
---

# Data Formats and Schemas

This guide provides a comprehensive reference for all data formats supported by fvctools, including the unified **Flyvercity Data Format (.fvc)** and external formats.

## Overview

fvctools works with multiple data formats:

1. **Flyvercity Data Format (.fvc)** - The unified format
2. **External formats** - Multiple aviation data formats
3. **Schema definitions** - JSON Schema for validation

## The Flyvercity Data Format (.fvc)

The **Flyvercity Data Format** is the **unified data standard** used by all fvctools.

### Format Specification

- **Type**: JSON-Lines (`.jsonl`)
- **Extension**: `.fvc`
- **Structure**: One record per line
- **First line**: METADATA record
- **Subsequent lines**: Data records

### Example

```json
{"content": "flightlog", "source": "nmea", "origin": "flight_data_20231201.log"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}}
{"time": {"unix": 1756033206883}, "pos": {"loc": {"lat": 52.3001, "lon": 4.9001, "alt": 100.8}}}
```

### File Structure

```
Line 1: METADATA record (describes file content)
Line 2+: Data records (actual flight/radar data)
```

### METADATA Record

The METADATA record is the **first line** of every `.fvc` file and describes:

- **content**: Type of data contained
- **source**: Original format the data was converted from
- **origin**: Name of the original source file or system

**METADATA Schema**:

```json
{
  "content": "flightlog",
  "source": "nmea",
  "origin": "flight_data.log"
}
```

**Content Types**:

| Content Type | Description | Data Records |
|--------------|-------------|--------------|
| `flightlog` | Flight log entries | FLIGHTLOG records |
| `radarlog` | Radar log entries | RADARLOG records |
| `fusion.replay` | Fusion engine replay events | FUSION_REPLAY records |
| `capture.message` | MQTT message captures | CAPTURE_MESSAGE records |

**Source Formats**:

| Source Format | Description |
|---------------|-------------|
| `nmea` | NMEA 0183 GPS protocol |
| `ulog` | PX4 ULog format |
| `safirmqtt` | SAFIR MQTT telemetry |
| `datcon` | DatCon flight recorder format |
| `senhive` | SenHive flight logging |
| `agentfly` | AgentFly simulator logs |
| `artlog` | ART log format |
| `courageous` | Courageous project logs |
| `csgroup` | CS Group logs |
| `gnettrack` | G-NetTrack GPS logs |
| `manna` | Manna flight logs |
| `robinradar` | Robin Radar system logs |
| `geojson` | GeoJSON geographic features |
| `kml` | KML Google Earth format |
| `fusion.replay` | Fusion engine replay |
| `capture.android` | Android MQTT capture |

### Data Record Types

#### 1. FLIGHTLOG Record

**Content Type**: `flightlog`

**Schema**:

```yaml
FLIGHTLOG:
  type: object
  properties:
    time:
      type: object
      properties:
        unix:
          type: integer
          description: Unix timestamp in milliseconds
        iso:
          type: string
          description: ISO 8601 formatted timestamp
      required:
        - unix
    pos:
      type: object
      properties:
        loc:
          type: object
          properties:
            lat:
              type: number
              minimum: -90
              maximum: 90
              description: Latitude in WGS-84
            lon:
              type: number
              minimum: -180
              maximum: 180
              description: Longitude in WGS-84
            alt:
              type: number
              description: Altitude in meters
            amsl:
              type: number
              description: Altitude above mean sea level
            height:
              type: number
              description: Height above ground
          required:
            - lat
            - lon
        attitude:
          type: object
          properties:
            roll:
              type: number
              description: Roll angle in degrees
            pitch:
              type: number
              description: Pitch angle in degrees
            yaw:
              type: number
              description: Yaw angle in degrees
        velocity:
          type: object
          properties:
            vx:
              type: number
              description: Velocity in X direction (m/s)
            vy:
              type: number
              description: Velocity in Y direction (m/s)
            vz:
              type: number
              description: Velocity in Z direction (m/s)
        gnss:
          type: object
          properties:
            satellites:
              type: integer
              description: Number of GNSS satellites
            hdop:
              type: number
              description: Horizontal dilution of precision
            vdop:
              type: number
              description: Vertical dilution of precision
            fix:
              type: string
              description: GNSS fix type
        cellular:
          type: object
          properties:
            imei:
              type: string
              description: IMEI of cellular device
            signal:
              type: integer
              description: Signal strength in dBm
      required:
        - time
        - pos
  required:
    - time
    - pos
```

**Example**:

```json
{
  "time": {"unix": 1756033206882, "iso": "2025-04-25T10:20:06.882Z"},
  "pos": {
    "loc": {
      "lat": 52.3,
      "lon": 4.9,
      "alt": 100.5,
      "amsl": 95.2,
      "height": 5.3
    },
    "attitude": {
      "roll": 2.5,
      "pitch": -1.2,
      "yaw": 45.0
    },
    "velocity": {
      "vx": 5.2,
      "vy": 3.1,
      "vz": 0.0
    },
    "gnss": {
      "satellites": 12,
      "hdop": 1.2,
      "vdop": 1.5,
      "fix": "3D"
    },
    "cellular": {
      "imei": "123456789012345",
      "signal": -75
    }
  }
}
```

#### 2. RADARLOG Record

**Content Type**: `radarlog`

**Schema**:

```yaml
RADARLOG:
  type: object
  properties:
    time:
      type: object
      properties:
        unix:
          type: integer
          description: Unix timestamp in milliseconds
      required:
        - unix
    pos:
      type: object
      oneOf:
        - properties:
            polar:
              type: object
              properties:
                azimuth:
                  type: number
                  description: Azimuth angle in degrees
                range:
                  type: number
                  description: Range in meters
                elevation:
                  type: number
                  description: Elevation angle in degrees
              required:
                - azimuth
                - range
          required:
            - polar
        - properties:
            loc:
              type: object
              properties:
                lat:
                  type: number
                  minimum: -90
                  maximum: 90
                lon:
                  type: number
                  minimum: -180
                  maximum: 180
              required:
                - lat
                - lon
          required:
            - loc
    rssi:
      type: number
      description: Received signal strength indicator in dBm
    angle:
      type: number
      description: Angle of arrival in degrees
  required:
    - time
    - pos
```

**Example (Polar Coordinates)**:

```json
{
  "time": {"unix": 1756033206882},
  "pos": {
    "polar": {
      "azimuth": 45.0,
      "range": 1000.0,
      "elevation": 10.5
    }
  },
  "rssi": -65,
  "angle": 45.2
}
```

**Example (Geographic Coordinates)**:

```json
{
  "time": {"unix": 1756033206882},
  "pos": {
    "loc": {
      "lat": 52.3,
      "lon": 4.9
    }
  },
  "rssi": -65,
  "angle": 45.2
}
```

#### 3. FUSION_REPLAY Record

**Content Type**: `fusion.replay`

**Schema**:

```yaml
FUSION_REPLAY:
  type: object
  properties:
    time:
      type: object
      properties:
        unix:
          type: integer
          description: Unix timestamp in milliseconds
      required:
        - unix
    event:
      type: string
      description: Type of fusion event
      enum: ["track_update", "track_lost", "track_gained", "fusion_error"]
    data:
      type: object
      description: Event-specific data
      properties:
        track_id:
          type: string
          description: Track identifier
        position:
          type: object
          properties:
            lat:
              type: number
            lon:
              type: number
            alt:
              type: number
        confidence:
          type: number
          description: Confidence score (0-1)
        message:
          type: string
          description: Human-readable message
      required:
        - track_id
  required:
    - time
    - event
```

**Example**:

```json
{
  "time": {"unix": 1756033206882},
  "event": "track_update",
  "data": {
    "track_id": "TRK-001",
    "position": {"lat": 52.3, "lon": 4.9, "alt": 100.5},
    "confidence": 0.95,
    "message": "Track updated with new position"
  }
}
```

#### 4. CAPTURE_MESSAGE Record

**Content Type**: `capture.message`

**Schema**:

```yaml
CAPTURE_MESSAGE:
  type: object
  properties:
    time:
      type: object
      properties:
        unix:
          type: integer
          description: Unix timestamp in milliseconds
      required:
        - unix
    topic:
      type: string
      description: MQTT topic
    payload:
      type: object
      description: Message payload
      properties:
        message_type:
          type: string
        data:
          type: object
        metadata:
          type: object
      required:
        - message_type
        - data
  required:
    - time
    - topic
    - payload
```

**Example**:

```json
{
  "time": {"unix": 1756033206882},
  "topic": "safir/telemetry/flight1",
  "payload": {
    "message_type": "POSITION_UPDATE",
    "data": {
      "latitude": 52.3,
      "longitude": 4.9,
      "altitude": 100.5
    },
    "metadata": {
      "source": "safir",
      "timestamp": "2025-04-25T10:20:06.882Z"
    }
  }
}
```

## External Data Formats

fvctools supports conversion from multiple external aviation data formats to the unified `.fvc` format.

### 1. NMEA 0183

**Module**: `nmea.py`

**Description**: Standard GPS protocol used by most GPS devices.

**Supported Sentence Types**:

- `GGA` - Global Positioning System Fix Data
- `RMC` - Recommended Minimum Specific GNSS Data
- `GSA` - GNSS DOP and Active Satellites
- `GSV` - GNSS Satellites in View

**Example NMEA Sentences**:

```
$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46
$GNRMC,123456.78,A,5234.1234,N,00450.1234,E,6.1,45.0,010123,0.0,E,A*1C
```

**Dependencies**:
- `pynmea2>=1.19.0`

**Conversion Command**:

```bash
fvc df --in flight.nmea convert nmea flight.fvc
```

**Related**: [NMEA Converter](/openwiki/architecture/data-formats.md#nmea-converter)

### 2. ULog (PX4)

**Module**: `ulog.py`

**Description**: Binary log format used by PX4 flight controllers.

**Supported Message Types**:

- `sensor_gps` - GPS data
- `vehicle_attitude` - Attitude information
- `vehicle_local_position` - Local position
- `vehicle_global_position` - Global position
- `system_time` - System time

**Example ULog File**: Contains multiple message types in binary format.

**Dependencies**:
- `pyulog>=1.2.2`

**Conversion Command**:

```bash
fvc df --in flight.ulg convert ulog flight.fvc
```

**Related**: [ULog Converter](/openwiki/architecture/data-formats.md#ulog-converter)

### 3. SAFIR MQTT

**Module**: `safirmqtt.py`, `safirmqtt_v2.py`

**Description**: Telemetry streaming using MQTT protocol.

**Message Topics**:

- `safir/telemetry/flight1`
- `safir/telemetry/flight2`
- `safir/status`

**Message Format**: JSON payload with flight data.

**Performance**:
- **v1**: Basic implementation
- **v2**: Optimized with Polars (commit cc7819d)

**Dependencies**:
- MQTT broker (Mosquitto, AWS IoT, etc.)

**Conversion Command**:

```bash
# From MQTT stream
mosquitto_sub -t "safir/telemetry" -v | \
python safir_converter.py

# Or from JSON file
fvc df --in telemetry.json convert safirmqtt_v2 output.fvc
```

**Related**: [SAFIR MQTT Converter](/openwiki/architecture/data-formats.md#safir-mqtt-converter)

### 4. DatCon

**Module**: `datcon.py`

**Description**: Flight recorder format used by some flight loggers.

**Features**:
- Binary format with structured data
- Multiple data channels
- Timestamped records

**Performance**:
- Optimized with Polars (commit b3858c6)

**Conversion Command**:

```bash
fvc df --in flight.datcon convert datcon flight.fvc
```

**Related**: [DatCon Converter](/openwiki/architecture/data-formats.md#datcon-converter)

### 5. SenHive

**Module**: `senhive.py`

**Description**: Flight logging system format.

**Features**:
- JSON-based format
- Multiple flight parameters
- Timestamped records

**Performance**:
- Optimized with Polars (commit a456910)

**Conversion Command**:

```bash
fvc df --in flight.senhive convert senhive flight.fvc
```

**Related**: [SenHive Converter](/openwiki/architecture/data-formats.md#senhive-converter)

### 6. AgentFly

**Module**: `agentfly.py`

**Description**: Simulator logs from AgentFly simulator.

**Features**:
- CSV format
- Flight parameters
- Waypoint data

**Performance**:
- Optimized with Polars (commit a456910)

**Conversion Command**:

```bash
fvc df --in flight.csv convert agentfly flight.fvc
```

**Related**: [AgentFly Converter](/openwiki/architecture/data-formats.md#agentfly-converter)

### 7. DJI

**Module**: `dji.py` (planned)

**Description**: DJI drone data format.

**Features**:
- Telemetry data
- Waypoint missions
- Camera metadata

**Conversion Command**:

```bash
fvc df --in dji_log.csv convert dji flight.fvc
```

### 8. GeoJSON

**Module**: `geojson.py`

**Description**: Standard geospatial data format.

**Supported Geometry Types**:

- Point
- LineString
- Polygon
- MultiPoint
- MultiLineString
- MultiPolygon

**Conversion Command**:

```bash
fvc df --in features.geojson convert geojson output.fvc
```

**Related**: [GeoJSON Converter](/openwiki/architecture/data-formats.md#geojson-converter)

### 9. KML

**Module**: `kml/` directory

**Description**: Google Earth KML format.

**Features**:
- Geographic features
- Placemarks
- Paths
- Polygons

**Conversion Command**:

```bash
fvc df --in features.kml convert kml output.fvc
```

**Output**: Can also export to KML for visualization

```bash
fvc render fl flight.fvc --output flight.kml --format kml
```

### 10. ART Log

**Module**: `artlog.py`

**Description**: ART log format.

**Features**:
- Text-based format
- Flight parameters
- Event logging

**Conversion Command**:

```bash
fvc df --in flight.art convert artlog flight.fvc
```

### 11. Courageous

**Module**: `courageous.py`

**Description**: Research flight logs from Courageous project.

**Features**:
- Structured text format
- Multiple data channels
- Timestamped records

**Conversion Command**:

```bash
fvc df --in flight.courageous convert courageous flight.fvc
```

### 12. CS Group

**Module**: `csgroup.py`

**Description**: CS Group radar and tracking logs.

**Features**:
- Radar track data
- Target information
- Timestamped detections

**Conversion Command**:

```bash
fvc df --in radar.log convert csgroup radar.fvc
```

### 13. G-NetTrack

**Module**: `gnettrack.py`

**Description**: GPS track logs from G-NetTrack.

**Features**:
- NMEA-based format
- GPS track data
- Waypoint information

**Conversion Command**:

```bash
fvc df --in track.gnettrack convert gnettrack track.fvc
```

### 14. Manna

**Module**: `manna.py`

**Description**: Manna flight logs.

**Features**:
- Structured text format
- Flight parameters
- Event logging

**Conversion Command**:

```bash
fvc df --in flight.manna convert manna flight.fvc
```

### 15. Robin Radar

**Module**: `robinradar.py`

**Description**: Robin Radar system logs.

**Features**:
- Radar system data
- Target tracking
- Signal processing

**Conversion Command**:

```bash
fvc df --in radar.log convert robinradar radar.fvc
```

## Format Converter Architecture

All format converters follow the same pattern:

```
External Format → Parser → Data Transformation → .fvc Writer → Output File
```

### Base Converter Class

```python
# /src/fvc/tools/df/xformats/base.py

from abc import ABC, abstractmethod

class BaseConverter(ABC):
    """Base class for all format converters"""
    
    @abstractmethod
    def convert(self, input_path: str, output_path: str) -> bool:
        """Convert input file to .fvc format"""
        pass
    
    def _write_metadata(self, output_path: str, content: str, source: str, origin: str) -> None:
        """Write METADATA record"""
        metadata = {
            "content": content,
            "source": source,
            "origin": origin,
        }
        with open(output_path, "w") as f:
            f.write(f"{metadata}\n")
    
    def _write_record(self, output_path: str, record: dict) -> None:
        """Write a single data record"""
        with open(output_path, "a") as f:
            f.write(f"{record}\n")
```

### Example: NMEA Converter

```python
# /src/fvc/tools/df/xformats/nmea.py

import pynmea2
from fvc.tools.df.xformats.base import BaseConverter

class NMEAConverter(BaseConverter):
    """Convert NMEA format to .fvc"""
    
    def convert(self, input_path: str, output_path: str) -> bool:
        # Write METADATA
        self._write_metadata(output_path, "flightlog", "nmea", input_path)
        
        # Parse NMEA sentences
        with open(input_path, "r") as f:
            for line in f:
                if line.startswith("$"):
                    try:
                        msg = pynmea2.parse(line)
                        record = self._nmea_to_record(msg)
                        self._write_record(output_path, record)
                    except Exception as e:
                        logger.warning(f"Failed to parse NMEA sentence: {e}")
                        continue
        
        return True
    
    def _nmea_to_record(self, msg: pynmea2.NMEASentence) -> dict:
        """Convert NMEA sentence to flightlog record"""
        return {
            "time": {"unix": int(msg.timestamp * 1000)},
            "pos": {
                "loc": {
                    "lat": msg.latitude,
                    "lon": msg.longitude,
                    "alt": msg.altitude if hasattr(msg, "altitude") else None,
                }
            }
        }
```

### Example: ULog Converter

```python
# /src/fvc/tools/df/xformats/ulog.py

import pyulog
from fvc.tools.df.xformats.base import BaseConverter

class ULogConverter(BaseConverter):
    """Convert ULog format to .fvc"""
    
    def convert(self, input_path: str, output_path: str) -> bool:
        # Write METADATA
        self._write_metadata(output_path, "flightlog", "ulog", input_path)
        
        # Parse ULog file
        ulog = pyulog.ULog(input_path)
        
        # Extract messages
        for msg in ulog.messages:
            if msg.name == "sensor_gps":
                record = self._gps_to_record(msg)
                self._write_record(output_path, record)
            elif msg.name == "vehicle_attitude":
                record = self._attitude_to_record(msg)
                self._write_record(output_path, record)
            # ... other message types
        
        return True
    
    def _gps_to_record(self, msg) -> dict:
        """Convert GPS message to flightlog record"""
        return {
            "time": {"unix": int(msg.data['time_boot_ms'])},
            "pos": {
                "loc": {
                    "lat": msg.data['lat'] / 1e7,
                    "lon": msg.data['lon'] / 1e7,
                    "alt": msg.data['alt'] / 1000.0,
                }
            }
        }
```

## Schema Validation

All .fvc files are validated against JSON schemas defined in `/src/fvc/tools/df/schema.yaml`.

### Schema Structure

```yaml
METADATA:
  type: object
  properties:
    content:
      type: string
      enum: [flightlog, radarlog, fusion.replay, capture.message]
    source:
      type: string
      # Multiple possible source formats
    origin:
      type: string
  required:
    - content
    - source
    - origin

FLIGHTLOG:
  type: object
  properties:
    time:
      type: object
      properties:
        unix:
          type: integer
      required:
        - unix
    pos:
      type: object
      properties:
        loc:
          type: object
          properties:
            lat:
              type: number
              minimum: -90
              maximum: 90
            lon:
              type: number
              minimum: -180
              maximum: 180
          required:
            - lat
            - lon
      required:
        - loc
  required:
    - time
    - pos

# ... other schemas
```

### Validation Process

```python
# /src/fvc/tools/df/schema.py

import json
from jsonschema import validate, ValidationError

class SchemaValidator:
    def __init__(self):
        self.schema = self._load_schema()
    
    def validate_file(self, file_path: str, verbose: bool = False) -> bool:
        """Validate .fvc file"""
        try:
            with open(file_path, "r") as f:
                # Validate METADATA (first line)
                metadata = json.loads(f.readline())
                self._validate_metadata(metadata)
                
                # Validate data records
                for line_num, line in enumerate(f, start=2):
                    record = json.loads(line)
                    content_type = metadata["content"]
                    self._validate_record(record, content_type, line_num)
            
            return True
        except json.JSONDecodeError as e:
            if verbose:
                print(f"Invalid JSON at line {line_num}: {e}")
            return False
        except ValidationError as e:
            if verbose:
                print(f"Validation error: {e.message}")
            return False
        except Exception as e:
            if verbose:
                print(f"Error: {e}")
            return False
```

### Validation Options

```bash
# Basic validation
fvc df --in file.fvc validate

# Verbose validation (shows errors)
fvc df --in file.fvc validate --verbose

# Strict validation (additional checks)
fvc df --in file.fvc validate --strict
```

## Data Quality and Validation

### 1. METADATA Validation

**Required fields**:
- `content`: Must be valid content type
- `source`: Must be valid source format
- `origin`: Must be non-empty string

**Content type consistency**: All data records must match METADATA content type.

### 2. Field Validation

**Required fields**:
- FLIGHTLOG: `time`, `pos`
- RADARLOG: `time`, `pos`
- FUSION_REPLAY: `time`, `event`
- CAPTURE_MESSAGE: `time`, `topic`, `payload`

**Type validation**:
- Numbers must be correct type
- Strings must match patterns
- Arrays must have correct items
- Objects must have required properties

**Range validation**:
- Latitude: -90 to 90
- Longitude: -180 to 180
- Altitude: No strict range (can be negative for below sea level)

### 3. Content Type Validation

**Content type determines record schema**:

```python
# From schema.py

def _validate_record(self, record: dict, expected_content: str, line_num: int):
    """Validate data record against expected content type"""
    if expected_content == "flightlog":
        validate(instance=record, schema=self.schema["FLIGHTLOG"])
    elif expected_content == "radarlog":
        validate(instance=record, schema=self.schema["RADARLOG"])
    # ... other content types
```

## Performance Considerations for Format Conversion

### 1. Use Polars for Data Processing

Recent commits show heavy use of Polars for performance:

```python
# /src/fvc/tools/df/xformats/agentfly.py

import polars as pl

class AgentFlyConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str) -> bool:
        # Read with Polars
        df = pl.read_csv(input_path)
        
        # Transform with Polars (lazy evaluation)
        df = (df
            .lazy()
            .with_columns(
                pl.col("timestamp").cast(pl.Int64),
                pl.col("latitude").cast(pl.Float32),  # Use Float32 for coordinates
            )
            .filter(pl.col("timestamp").is_not_null())
            .collect()
        )
        
        # Write to .fvc
        self._write_fvc(df, output_path)
        return True
```

### 2. Streaming for Large Files

For very large files, use streaming:

```python
# Process line by line
with open("large_file.jsonl", "r") as f:
    for line in f:
        record = json.loads(line)
        process_record(record)
```

### 3. Memory Management

**Techniques**:

- ✅ Use appropriate data types (Float32 instead of Float64)
- ✅ Use lazy evaluation with Polars
- ✅ Process in chunks for very large files
- ✅ Close files properly with context managers

### 4. Parallel Processing

**Techniques**:

- ✅ Use Polars parallel operations
- ✅ Use GNU parallel for batch processing
- ✅ Use multiprocessing for CPU-bound tasks

```bash
# Parallel batch processing
find ./input -name "*.nmea" | parallel -j $(nproc) fvc df --in {} convert nmea {.}.fvc
```

## Format Conversion Workflows

### 1. Single File Conversion

```bash
# Convert NMEA to .fvc
fvc df --in flight.nmea convert nmea flight.fvc

# Validate output
fvc df --in flight.fvc validate
```

### 2. Batch Conversion

```bash
# Convert all NMEA files in directory
for file in ./input/*.nmea; do
    output="./output/${file%.*}.fvc"
    fvc df --in "$file" convert nmea "$output"
    fvc df --in "$output" validate
done
```

### 3. Parallel Batch Conversion

```bash
# Using GNU parallel
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc && \
   fvc df --in {.}.fvc validate'
```

### 4. Conversion Pipeline

```bash
# Full pipeline: Convert → Validate → Analyze → Visualize
fvc df --in flight.nmea convert nmea flight.fvc && \
fvc df --in flight.fvc validate && \
fvc tools flightlog stats flight.fvc > stats.txt && \
fvc render fl flight.fvc --output ./map
```

## Schema Documentation Generation

The schema documentation is **automatically generated** from `/src/fvc/tools/df/schema.yaml`:

```bash
# Generate schema docs
python scripts/generate_schema_docs.py

# Output goes to /docs/schema/
```

**Generated files**:
- `/docs/schema/METADATA.md`
- `/docs/schema/FLIGHTLOG.md`
- `/docs/schema/RADARLOG.md`
- `/docs/schema/FUSION_REPLAY.md`
- `/docs/schema/CAPTURE_MESSAGE.md`

**See**: [Schema Documentation](/docs/schema/README.md)

## External Format Reference

### NMEA Sentence Reference

| Sentence | Description | Key Fields |
|----------|-------------|------------|
| GGA | Global Positioning System Fix Data | lat, lon, alt, satellites, hdop |
| RMC | Recommended Minimum Specific GNSS Data | lat, lon, speed, course, date |
| GSA | GNSS DOP and Active Satellites | pdop, hdop, vdop, satellites |
| GSV | GNSS Satellites in View | satellites, azimuth, elevation, snr |

**Example GGA Sentence**:
```
$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46
```

**Parsed fields**:
- Time: 123456.78
- Latitude: 52°34.1234'N = 52.568723°
- Longitude: 004°50.1234'E = 4.835390°
- Quality: 1 (GPS fix)
- Satellites: 12
- HDOP: 1.2
- Altitude: 100.5m
- Geoid separation: 48.2m

### ULog Message Reference

| Message Type | Description | Key Fields |
|--------------|-------------|------------|
| sensor_gps | GPS sensor data | lat, lon, alt, satellites, fix |
| vehicle_attitude | Attitude information | roll, pitch, yaw |
| vehicle_local_position | Local position | x, y, z, vx, vy, vz |
| vehicle_global_position | Global position | lat, lon, alt, vel |
| system_time | System time | time_boot_ms |

**Example**: See ULog converter implementation.

## Troubleshooting Format Issues

### 1. Format Not Recognized

**Error**: `ValueError: Unknown format: xxx`

**Solutions**:
- Check format name is correct
- Verify format is supported
- Add format converter if needed

```bash
# Check supported formats
fvc df convert --help
```

### 2. Conversion Fails

**Error**: Conversion command fails with no output

**Debugging steps**:

```bash
# Check input file
ls -la input.nmea
head -n 5 input.nmea

# Try verbose mode
fvc df --in input.nmea convert nmea output.fvc --verbose

# Check logs
cat fvctools.log | grep ERROR
```

**Common causes**:
- Invalid input format
- Missing dependencies
- Permission issues
- Schema validation failures

### 3. Schema Validation Fails

**Error**: `ValidationError: <reason>`

**Debugging steps**:

```bash
# Check METADATA
head -n 1 output.fvc | jq .

# Check data records
jq 'select(.time == null)' output.fvc

# Validate with verbose output
fvc df --in output.fvc validate --verbose
```

**Common causes**:
- METADATA is missing or invalid
- Content type mismatch
- Missing required fields
- Invalid field types
- Range violations

### 4. Data Quality Issues

**Error**: Output data doesn't match expectations

**Debugging steps**:

```bash
# Check input data
head -n 10 input.nmea

# Check output data
head -n 10 output.fvc

# Compare input and output
# Verify conversion logic
```

**Common causes**:
- Incorrect field mapping
- Unit conversion errors
- Timestamp handling issues
- Missing data handling

## Format Conversion Best Practices

### 1. Always Validate Output

```bash
# Convert and validate
fvc df --in input.nmea convert nmea output.fvc
fvc df --in output.fvc validate
```

### 2. Use Verbose Mode for Debugging

```bash
fvc df --in input.nmea convert nmea output.fvc --verbose
```

### 3. Document Format-Specific Quirks

```markdown
# NMEA Format Notes

## Quirks
- Altitude in GGA sentence is in meters
- Latitude/Longitude are in DMM format (degrees and decimal minutes)
- Need to convert from DMM to DD

## Example
Input: $GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46
Parsed: lat=52.568723, lon=4.835390, alt=100.5
```

### 4. Handle Edge Cases

```python
# In converter code
try:
    msg = pynmea2.parse(line)
    record = self._nmea_to_record(msg)
    self._write_record(output_path, record)
except Exception as e:
    logger.warning(f"Failed to parse NMEA sentence: {e}")
    continue  # Skip invalid sentence
```

### 5. Test with Real Data

```bash
# Test with sample files
fvc df --in sample.nmea convert nmea sample.fvc
fvc df --in sample.fvc validate

# Compare with expected output
# Verify data quality
```

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Conversion Workflows](/openwiki/workflows/conversion.md)
- [Validation Workflows](/openwiki/workflows/validation.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Schema Documentation](/docs/schema/README.md)
- [Architecture Overview](/openwiki/architecture/overview.md)

## Quick Reference

| Format | Module | Command | Content Type |
|--------|--------|---------|--------------|
| NMEA | `nmea.py` | `fvc df convert nmea` | flightlog |
| ULog | `ulog.py` | `fvc df convert ulog` | flightlog |
| SAFIR MQTT | `safirmqtt.py` | `fvc df convert safirmqtt` | flightlog |
| DatCon | `datcon.py` | `fvc df convert datcon` | flightlog |
| SenHive | `senhive.py` | `fvc df convert senhive` | flightlog |
| AgentFly | `agentfly.py` | `fvc df convert agentfly` | flightlog |
| GeoJSON | `geojson.py` | `fvc df convert geojson` | flightlog/radarlog |
| KML | `kml/` | `fvc df convert kml` | flightlog/radarlog |
| ART | `artlog.py` | `fvc df convert artlog` | flightlog |
| Courageous | `courageous.py` | `fvc df convert courageous` | flightlog |
| CS Group | `csgroup.py` | `fvc df convert csgroup` | radarlog |
| G-NetTrack | `gnettrack.py` | `fvc df convert gnettrack` | flightlog |
| Manna | `manna.py` | `fvc df convert manna` | flightlog |
| Robin Radar | `robinradar.py` | `fvc df convert robinradar` | radarlog |

## Best Practices Summary

✅ **Use .fvc as unified format** for all operations
✅ **Validate METADATA** is correct and first line
✅ **Validate content type consistency** across all records
✅ **Use Polars** for performance-critical conversions
✅ **Handle edge cases** gracefully (nulls, invalid data)
✅ **Document format-specific quirks**
✅ **Test with real data** before deployment
✅ **Use verbose mode** for debugging
✅ **Always validate output** after conversion
✅ **Use appropriate data types** (Float32 for coordinates)
✅ **Monitor performance** and optimize hot paths

## Next Steps

- **Learn about conversion workflows**: [/openwiki/workflows/conversion.md](/openwiki/workflows/conversion.md)
- **Set up validation**: [/openwiki/workflows/validation.md](/openwiki/workflows/validation.md)
- **Explore CLI tools**: [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md)
- **Check schema documentation**: [/docs/schema/README.md](/docs/schema/README.md)
- **Run format converters**: Try converting sample files
