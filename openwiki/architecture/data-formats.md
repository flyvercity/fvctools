---
type: Data Formats Guide
title: Data Formats and Schemas

description: Comprehensive reference for the Flyvercity Data Format (.fvc) and all supported external formats, including schema details and examples

resource: /src/fvc/tools/df/schema.yaml

tags: [data-formats, schemas, fvc, json-lines, validation]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T12:24:16.401Z
sources:
  - id: openwiki-source-e1ac5460a2f3e3c6f12f34a1
    resource: repo://src/fvc/tools/df/core.py
  - id: openwiki-source-46d742c2ece6c8c74339767d
    resource: repo://src/fvc/tools/df/schema.py
  - id: openwiki-source-fc5776122634f6b1b77cbd0c
    resource: repo://src/fvc/tools/df/schema.yaml
  - id: openwiki-source-4ac6699f79ea2f0f545f3b19
    resource: repo://src/fvc/tools/df/xformats/nmea.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T12:24:16.401Z" }
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

**Schema** (from `/src/fvc/tools/df/schema.yaml`):

```yaml
FLIGHTLOG:
  $title: "Flight Log Entry"
  type: object
  properties:
    origin:
      type: string
      description: "Originating system"
      examples: ["airlink", "courageous", "nmea"]
    time:
      description: "Timestamp of the flight log entry"
      type: object
      properties:
        unix:
          type: number
          description: "Unix timestamp in milliseconds"
          examples: [1756033206882]
        rx:
          type: number
          description: "Reception timestamp in milliseconds"
          examples: [1756033207094]
        original:
          type: string
          description: "Original timestamp string"
          examples: ["2025-01-01 12:00:00"]
      required:
        - unix
    uaid:
      description: "Unique aircraft identification"
      type: object
      properties:
        int:
          type: string
          description: "Source-internal identifier"
          examples: ["FL001"]
        fvc:
          type: string
          description: "Flyvercity unique identifier"
          examples: ["fvc-abc123"]
        icaohex:
          type: string
          description: "ICAO 24-bit address"
          examples: ["ABC123"]
        icaoreg:
          type: string
          description: "ICAO registration"
          examples: ["N123AB"]
      anyOf:
        - required: [int]
        - required: [fvc]
    pos:
      description: "Aircraft position and attitude"
      type: object
      properties:
        loc:
          description: "Geographic location"
          type: object
          properties:
            lat:
              type: number
              description: "Latitude in WGS-84"
              examples: [55.7558]
            lon:
              type: number
              description: "Longitude in WGS-84"
              examples: [37.6176]
            alt:
              type: number
              description: "Ellipsoidal altitude"
              examples: [100.5]
            amsl:
              type: number
              description: "Altitude above mean sea level"
              examples: [95.2]
            height:
              type: number
              description: "Local height above ground"
              examples: [10.5]
            bear:
              type: number
              description: "Bearing angle in degrees clockwise from true north"
              examples: [45.0]
            gspeed:
              type: number
              description: "Ground speed in meters per second"
              examples: [15.5]
          required:
            - lat
            - lon
        att:
          description: "Aircraft attitude"
          type: object
          properties:
            roll:
              type: number
              description: "Roll angle in degrees"
              examples: [-30.0, 0.0, 15.5]
            pitch:
              type: number
              description: "Pitch angle in degrees"
              examples: [-10.0, 0.0, 20.0]
            yaw:
              type: number
              description: "Yaw angle in degrees"
              examples: [0.0, 90.0, 180.0]
          required:
            - roll
            - pitch
            - yaw
      required:
        - loc
    cellsig:
      description: "Cellular signal information"
      type: object
      properties:
        radio:
          type: string
          description: "Radio technology type"
          enum: [Unknown, 2G3G, 4GLTE, 5GNSA, 5GNR]
          examples: ["4GLTE"]
        rsrp:
          type: number
          description: "Reference Signal Received Power (dBm)"
          examples: [-80]
        rsrq:
          type: number
          description: "Reference Signal Received Quality (dB)"
          examples: [-10]
        rssi:
          type: number
          description: "Received Signal Strength Indicator (dBm)"
          examples: [-70]
        sinr:
          type: number
          description: "Signal-to-Interference-plus-Noise Ratio (dB)"
          examples: [10]
      additionalProperties: false
    gnss:
      type: object
      description: "GNSS constellation satellite counts"
      properties:
        gps:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
        glonass:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
        galileo:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
        beidou:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
        qzss:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
        irnss:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
        sbas:
          type: object
          properties:
            in_view:
              type: number
            used:
              type: number
    metadata:
      type: object
      description: "Additional metadata"
  required:
    - time
    - pos
  additionalProperties: false
```

**Example**:

```json
{
  "time": {"unix": 1756033206882, "rx": 1756033207094},
  "pos": {
    "loc": {
      "lat": 52.3,
      "lon": 4.9,
      "alt": 100.5,
      "amsl": 95.2,
      "height": 5.3,
      "bear": 45.0,
      "gspeed": 15.5
    },
    "att": {
      "roll": 2.5,
      "pitch": -1.2,
      "yaw": 45.0
    }
  },
  "cellsig": {
    "radio": "4GLTE",
    "rsrp": -75,
    "rsrq": -12,
    "rssi": -70,
    "sinr": 15
  },
  "gnss": {
    "gps": {"in_view": 12, "used": 10},
    "glonass": {"in_view": 8, "used": 6}
  }
}
```

#### 2. RADARLOG Record

**Content Type**: `radarlog`

**Schema** (from `/src/fvc/tools/df/schema.yaml`):

```yaml
RADARLOG:
  $title: "Radar Log Entry"
  type: object
  properties:
    origin:
      type: string
      description: "Originating system"
      examples: ["robinradar", "csgroup", "senhive"]
    time:
      description: "Timestamp of the radar log entry"
      type: object
      properties:
        unix:
          type: number
          description: "Unix timestamp in milliseconds"
          examples: [1756033206882]
        rx:
          type: number
          description: "Reception timestamp in milliseconds"
          examples: [1756033207094]
        original:
          type: string
          description: "Original timestamp string"
          examples: ["2025-01-01 12:00:00"]
      required:
        - unix
    uaid:
      description: "Unique aircraft identification"
      type: object
      properties:
        int:
          type: string
          examples: ["TRK-001"]
        fvc:
          type: string
          examples: ["fvc-xyz789"]
        icaohex:
          type: string
          examples: ["ABC123"]
        icaoreg:
          type: string
          examples: ["N123AB"]
      anyOf:
        - required: [int]
        - required: [fvc]
    pos:
      description: "Radar position information"
      type: object
      properties:
        loc:
          description: "Polar coordinates"
          type: object
          properties:
            bear:
              type: number
              description: "Bearing angle in degrees"
              examples: [45.0]
            elev:
              type: number
              description: "Elevation angle in degrees"
              examples: [10.5]
          required:
            - bear
            - elev
      required:
        - loc
  required:
    - time
    - pos
  additionalProperties: false
```

**Example (Polar Coordinates)**:

```json
{
  "time": {"unix": 1756033206882},
  "pos": {
    "loc": {
      "bear": 45.0,
      "elev": 10.5
    }
  }
}
```

#### 3. FUSION_REPLAY Record

**Content Type**: `fusion.replay`

**Schema** (from `/src/fvc/tools/df/schema.yaml`):

```yaml
FUSION_REPLAY:
  $title: "Fusion Replay Event"
  type: object
  properties:
    event:
      type: string
      description: "Event type"
      enum: [launch, start, stop, input, output, error]
      examples: ["start", "input", "output"]
    cycle:
      type: number
      description: "Cycle number"
      examples: [1, 100, 1000]
    origin:
      type: string
      description: "Originating network or system"
      examples: ["safesky"]
    message:
      type: object
      description: "Event message payload"
    metadata:
      type: object
      description: "Event metadata"
  required:
    - event
    - cycle
  additionalProperties: false
```

**Example**:

```json
{
  "time": {"unix": 1756033206882},
  "event": "start",
  "cycle": 1,
  "origin": "safesky",
  "message": {
    "track_id": "TRK-001",
    "position": {"lat": 52.3, "lon": 4.9, "alt": 100.5},
    "confidence": 0.95
  }
}
```

#### 4. CAPTURE_MESSAGE Record

**Content Type**: `capture.message`

**Schema** (from `/src/fvc/tools/df/schema.yaml`):

```yaml
CAPTURE_MESSAGE:
  $title: "Captured Message"
  type: object
  description: "Messages captured from MQTT topics"
  properties:
    mqtt:
      type: object
      description: "MQTT Metadata"
      properties:
        time:
          description: "MQTT message timestamp"
          type: object
          properties:
            unix:
              type: number
              examples: [1756033206882]
            rx:
              type: number
              examples: [1756033207094]
            original:
              type: string
              examples: ["2025-01-01 12:00:00"]
          required:
            - time
            - topic
        topic:
          type: string
          description: "MQTT topic"
          examples: ["/aircraft/position", "/radar/track"]
      required:
        - time
        - topic
      additionalProperties: false
  required:
    - mqtt
  additionalProperties: true
```

**Example**:

```json
{
  "mqtt": {
    "time": {"unix": 1756033206882},
    "topic": "safir/telemetry/flight1",
    "payload": {
      "message_type": "POSITION_UPDATE",
      "data": {
        "latitude": 52.3,
        "longitude": 4.9,
        "altitude": 100.5
      }
    }
  }
}
```

## External Data Formats

fvctools supports conversion from multiple external aviation data formats to the unified `.fvc` format.

### 1. NMEA 0183

**Module**: `fvc.tools.df.xformats.nmea`

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
- `python-dateutil`

**Conversion Command**:

```bash
fvc df --in flight.nmea convert nmea flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/nmea.py`

**Related**: [NMEA Standard](https://www.nmea.org/)

### 2. ULog (PX4)

**Module**: `fvc.tools.df.xformats.ulog`

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

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/ulog.py`

**Related**: [PX4 ULog Documentation](https://docs.px4.io/main/en/log/ulog_file_format.html)

### 3. SAFIR MQTT

**Module**: `fvc.tools.df.xformats.safirmqtt`, `fvc.tools.df.xformats.safirmqtt_v2`

**Description**: Telemetry streaming using MQTT protocol.

**Message Topics**:

- `safir/telemetry/flight1`
- `safir/telemetry/flight2`
- `safir/status`

**Message Format**: JSON payload with flight data.

**Performance**:
- **v1**: Basic implementation
- **v2**: Optimized with JSON processing

**Dependencies**:
- MQTT broker (Mosquitto, AWS IoT, etc.)

**Conversion Command**:

```bash
# From MQTT stream
mosquitto_sub -t "safir/telemetry" -v | \
python safir_converter.py

# Or from JSON file
fvc df --in telemetry.json convert safirmqtt output.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/safirmqtt.py`

### 4. DatCon

**Module**: `fvc.tools.df.xformats.datcon`

**Description**: Flight recorder format used by some flight loggers.

**Features**:
- Binary format with structured data
- Multiple data channels
- Timestamped records

**Conversion Command**:

```bash
fvc df --in flight.datcon convert datcon flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/datcon.py`

### 5. SenHive

**Module**: `fvc.tools.df.xformats.senhive`

**Description**: Flight logging system format.

**Features**:
- JSON-based format
- Multiple flight parameters
- Timestamped records

**Conversion Command**:

```bash
fvc df --in flight.senhive convert senhive flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/senhive.py`

### 6. AgentFly

**Module**: `fvc.tools.df.xformats.agentfly`

**Description**: Simulator logs from AgentFly simulator.

**Features**:
- CSV format
- Flight parameters
- Waypoint data

**Conversion Command**:

```bash
fvc df --in flight.csv convert agentfly flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/agentfly.py`

### 7. DJI

**Module**: `fvc.tools.df.xformats.dji` (planned)

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

**Module**: `fvc.tools.df.xformats.geojson`

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

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/geojson.py`

### 9. KML

**Module**: `fvc.tools.df.xformats.kml` directory

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

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/kml/__init__.py`

**Output**: Can also export to KML for visualization

```bash
fvc render fl flight.fvc --output flight.kml --format kml
```

### 10. ART Log

**Module**: `fvc.tools.df.xformats.artlog`

**Description**: ART log format.

**Features**:
- Text-based format
- Flight parameters
- Event logging

**Conversion Command**:

```bash
fvc df --in flight.art convert artlog flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df/xformats/artlog.py`

### 11. Courageous

**Module**: `fvc.tools.df.xformats.courageous`

**Description**: Research flight logs from Courageous project.

**Features**:
- Structured text format
- Multiple data channels
- Timestamped records

**Conversion Command**:

```bash
fvc df --in flight.courageous convert courageous flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools.df.xformats.courageous.py`

### 12. CS Group

**Module**: `fvc.tools.df.xformats.csgroup`

**Description**: CS Group radar and tracking logs.

**Features**:
- Radar track data
- Target information
- Timestamped detections

**Conversion Command**:

```bash
fvc df --in radar.log convert csgroup radar.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df.xformats/csgroup.py`

### 13. G-NetTrack

**Module**: `fvc.tools.df.xformats.gnettrack`

**Description**: GPS track logs from G-NetTrack.

**Features**:
- NMEA-based format
- GPS track data
- Waypoint information

**Conversion Command**:

```bash
fvc df --in track.gnettrack convert gnettrack track.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df.xformats/gnettrack.py`

### 14. Manna

**Module**: `fvc.tools.df.xformats.manna`

**Description**: Manna flight logs.

**Features**:
- Structured text format
- Flight parameters
- Event logging

**Conversion Command**:

```bash
fvc df --in flight.manna convert manna flight.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df.xformats/manna.py`

### 15. Robin Radar

**Module**: `fvc.tools.df.xformats.robinradar`

**Description**: Robin Radar system logs.

**Features**:
- Radar system data
- Target tracking
- Signal processing

**Conversion Command**:

```bash
fvc df --in radar.log convert robinradar radar.fvc
```

**Converter Function**: `convert_to_fvc()` in `/src/fvc/tools/df.xformats/robinradar.py`

## Format Converter Architecture

All format converters follow the same pattern:

```
External Format → convert_to_fvc() function → .fvc Writer → Output File
```

### Conversion Process Flow

```python
# From /src/fvc/tools/df/core.py

def convert(params: DFParams):
    """Convert external format to FVC format"""
    # 1. Import the external format module
    ext_format_mod = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')
    
    # 2. Get the conversion function
    convert_fun = getattr(ext_format_mod, 'convert_to_fvc')
    
    # 3. Create metadata
    meta = metadata.create_metadata(input_path.name, params)
    
    # 4. Call converter with metadata, input, and output
    with dfu.JsonlinesIO(output_path, 'w') as io:
        convert_fun(params, meta, input_path, io)
```

### Example: NMEA Converter

```python
# From /src/fvc/tools/df/xformats/nmea.py
def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    """Convert NMEA format to .fvc"""
    
    # Update metadata with format-specific info
    metadata.update({
        'content': 'flightlog',
        'source': 'nmea',
    })
    
    # Write METADATA
    output.write(metadata)
    
    # Parse NMEA sentences
    with open(input_path, "r") as f:
        for line in f:
            if line.startswith("$"):
                try:
                    msg = pynmea2.parse(line)
                    record = {
                        "time": {"unix": int(msg.timestamp * 1000)},
                        "pos": {
                            "loc": {
                                "lat": msg.latitude,
                                "lon": msg.longitude,
                                "alt": msg.altitude if hasattr(msg, "altitude") else None,
                            }
                        }
                    }
                    output.write(record)
                except Exception as e:
                    lg.warning(f"Failed to parse NMEA sentence: {e}")
                    continue
```

### Example: ULog Converter

```python
# From /src/fvc/tools/df/xformats/ulog.py
def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    """Convert ULog format to .fvc"""
    
    # Update metadata
    metadata.update({
        'content': 'flightlog',
        'source': 'ulog',
    })
    
    # Write METADATA
    output.write(metadata)
    
    # Parse ULog file
    ulog = pyulog.ULog(input_path)
    
    # Extract messages
    for msg in ulog.messages:
        if msg.name == "sensor_gps":
            record = {
                "time": {"unix": int(msg.data['time_boot_ms'])},
                "pos": {
                    "loc": {
                        "lat": msg.data['lat'] / 1e7,
                        "lon": msg.data['lon'] / 1e7,
                        "alt": msg.data['alt'] / 1000.0,
                    }
                }
            }
            output.write(record)
        # ... other message types
```

## Schema Validation

All .fvc files are validated against JSON schemas defined in `/src/fvc/tools/df/schema.yaml`.

### Schema Structure

The schema is defined using JSON Schema with reusable components:

```yaml
# From /src/fvc/tools/df/schema.yaml

# Reusable components (anchors)
LOCATION: &LOCATION
  type: object
  properties:
    lat: {type: number, description: "Latitude in WGS-84"}
    lon: {type: number, description: "Longitude in WGS-84"}
    # ... other location fields
  required: [lat, lon]

TIMESTAMP: &TIMESTAMP
  type: object
  properties:
    unix: {type: number, description: "Unix timestamp in milliseconds"}
    rx: {type: number, description: "Reception timestamp"}
    original: {type: string, description: "Original timestamp string"}
  required: [unix]

# Content-specific schemas using anchors
FLIGHTLOG:
  type: object
  properties:
    time: {allOf: [*TIMESTAMP]}
    pos: {allOf: [*POSITION]}
    # ... other flightlog fields
  required: [time, pos]

METADATA:
  type: object
  properties:
    content: {type: string, enum: [flightlog, radarlog, fusion.replay, capture.message]}
    source: {type: string, description: "Original data format"}
    origin: {type: string, description: "Original file name"}
  required: [content, source, origin]

# Mapping of content types to schemas
CONTENT_SCHEMA:
  flightlog: *FLIGHTLOG
  radarlog: *RADARLOG
  fusion.replay: *FUSION_REPLAY
  capture.message: *CAPTURE_MESSAGE
```

### Validation Process

```python
# From /src/fvc/tools/df/core.py
def validate(input_path: Path) -> bool:
    with dfu.JsonlinesIO(input_path, 'r', raw=True) as f:
        # 1. Validate METADATA (first line)
        metaline = f.read()
        jsonschema.validate(metaline, schema.METADATA)
        content = metaline['content']
        
        # 2. Get schema for content type
        if content not in schema.CONTENT_SCHEMA:
            raise UserWarning(f'Unknown content type: {content}')
        
        content_schema = schema.CONTENT_SCHEMA[content]
        
        # 3. Create validator for content type
        cls = jsonschema.validators.validator_for(content_schema)
        validator = cls(content_schema)
        
        # 4. Validate each data record
        for data in f.iterate():
            validator.validate(data)
    
    return True
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
- `content`: Must be valid content type (flightlog, radarlog, fusion.replay, capture.message)
- `source`: Must be valid source format
- `origin`: Must be non-empty string

**Content type consistency**: All data records must match METADATA content type.

### 2. Field Validation

**Required fields**:
- FLIGHTLOG: `time`, `pos`
- RADARLOG: `time`, `pos`
- FUSION_REPLAY: `event`, `cycle`
- CAPTURE_MESSAGE: `mqtt` (with `time` and `topic`)

**Type validation**:
- Numbers must be correct type
- Strings must match patterns
- Objects must have required properties

**Range validation**:
- Latitude: -90 to 90
- Longitude: -180 to 180
- Altitude: No strict range (can be negative for below sea level)

### 3. Content Type Validation

**Content type determines record schema**:

```python
# From core.py validation
content_schema = schema.CONTENT_SCHEMA[content]
validator = jsonschema.Draft7Validator(content_schema)
validator.validate(data_record)
```

## Performance Considerations for Format Conversion

### 1. Streaming for Large Files

All converters use streaming to handle large files efficiently:

```python
# From nmea.py converter
with open(input_path, "r") as f:
    for line in f:
        if line.startswith("$"):
            try:
                msg = pynmea2.parse(line)
                record = self._nmea_to_record(msg)
                output.write(record)
            except Exception as e:
                continue  # Skip invalid sentence
```

### 2. Memory Management

**Techniques**:

- ✅ Use appropriate data types (Float32 for coordinates where possible)
- ✅ Process in chunks for very large files
- ✅ Close files properly with context managers
- ✅ Stream data line by line instead of loading entire files

### 3. Parallel Processing

**Techniques**:

- ✅ Use GNU parallel for batch processing
- ✅ Use multiprocessing for CPU-bound tasks

```bash
# Parallel batch processing
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc && \
   fvc df --in {.}.fvc validate'
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
    output.write(record)
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
| NMEA | `xformats.nmea` | `fvc df convert nmea` | flightlog |
| ULog | `xformats.ulog` | `fvc df convert ulog` | flightlog |
| SAFIR MQTT | `xformats.safirmqtt` | `fvc df convert safirmqtt` | flightlog |
| DatCon | `xformats.datcon` | `fvc df convert datcon` | flightlog |
| SenHive | `xformats.senhive` | `fvc df convert senhive` | flightlog |
| AgentFly | `xformats.agentfly` | `fvc df convert agentfly` | flightlog |
| GeoJSON | `xformats.geojson` | `fvc df convert geojson` | flightlog/radarlog |
| KML | `xformats.kml` | `fvc df convert kml` | flightlog/radarlog |
| ART | `xformats.artlog` | `fvc df convert artlog` | flightlog |
| Courageous | `xformats.courageous` | `fvc df convert courageous` | flightlog |
| CS Group | `xformats.csgroup` | `fvc df convert csgroup` | radarlog |
| G-NetTrack | `xformats.gnettrack` | `fvc df convert gnettrack` | flightlog |
| Manna | `xformats.manna` | `fvc df convert manna` | flightlog |
| Robin Radar | `xformats.robinradar` | `fvc df convert robinradar` | radarlog |

## Best Practices Summary

✅ **Use .fvc as unified format** for all operations
✅ **Validate METADATA** is correct and first line
✅ **Validate content type consistency** across all records
✅ **Handle edge cases** gracefully (nulls, invalid data)
✅ **Document format-specific quirks**
✅ **Test with real data** before deployment
✅ **Use verbose mode** for debugging
✅ **Always validate output** after conversion
✅ **Use appropriate data types** (Float32 for coordinates where possible)
✅ **Monitor performance** and optimize hot paths
✅ **Use streaming** for large files

## Next Steps

- **Learn about conversion workflows**: [/openwiki/workflows/conversion.md](/openwiki/workflows/conversion.md)
- **Set up validation**: [/openwiki/workflows/validation.md](/openwiki/workflows/validation.md)
- **Explore CLI tools**: [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md)
- **Check schema documentation**: [/docs/schema/README.md](/docs/schema/README.md)
- **Run format converters**: Try converting sample files
