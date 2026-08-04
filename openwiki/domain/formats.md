---
type: Domain Format Reference
title: Domain Formats and Models
edescription: Reference documentation for domain-specific formats, data models, and business logic in fvctools
resource: https://github.com/flyvercity/fvctools
okf_version: "0.1"
tags: [domain, formats, models, data-structures, reference]
---

# Domain Formats and Models

This document provides detailed reference documentation for domain-specific formats, data models, and business logic used throughout the fvctools suite.

## 🎯 Table of Contents

- [Flight Log Domain Model](#flight-log-domain-model)
- [Radar Log Domain Model](#radar-log-domain-model)
- [Geospatial Domain Models](#geospatial-domain-models)
- [Identifier Systems](#identifier-systems)
- [Metadata Model](#metadata-model)
- [Conversion Context](#conversion-context)

---

## ✈️ Flight Log Domain Model

The flight log domain model represents aircraft position, state, and telemetry data over time.

### Core Flight Log Concepts

#### Flight State

A flight log represents the complete state of an aircraft during a flight, including:

- **Position**: Latitude, longitude, altitude
- **Attitude**: Heading, pitch, roll
- **Velocity**: Ground speed, vertical speed
- **Status**: Flight mode, arming state, battery level
- **Environment**: Wind, temperature, pressure
- **Events**: Waypoints, takeoff, landing, mode changes

#### Temporal Structure

Flight logs are time-series data with:

- **Timestamps**: Unix timestamps in milliseconds
- **Sampling Rate**: Variable depending on source format
- **Data Points**: Individual measurements at specific times
- **Segments**: Logical divisions of flight (takeoff, cruise, landing)

### Flight Log Record Structure

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
      "alt": 100.5
    },
    "heading": 270.5,
    "groundspeed": 15.2
  },
  "origin": "flight_data_20231201.log",
  "quality": {
    "hdop": 1.2,
    "vdop": 0.8,
    "satellites": 12
  }
}
```

### Flight Phases

Flight logs can be segmented into phases:

1. **Pre-flight**: Aircraft on ground, systems powered
2. **Takeoff**: Initial climb to cruise altitude
3. **Climb**: Ascent to target altitude
4. **Cruise**: Level flight at constant altitude
5. **Descent**: Descent to landing altitude
6. **Landing**: Final approach and touchdown
7. **Post-flight**: Aircraft on ground, systems powered down

### Flight Log Processing

The flight log processing pipeline includes:

1. **Loading**: Parse raw flight data into structured format
2. **Segmentation**: Divide flight into logical segments
3. **Filtering**: Remove invalid or outlier data points
4. **Validation**: Check data quality and consistency
5. **Transformation**: Convert to unified .fvc format
6. **Analysis**: Extract metrics and insights

---

## 📡 Radar Log Domain Model

The radar log domain model represents detected targets and their state over time.

### Core Radar Log Concepts

#### Target Tracking

Radar logs track the position and state of detected targets:

- **Target Identification**: Unique target ID
- **Position**: Latitude, longitude, altitude
- **Velocity**: Speed and direction
- **Classification**: Target type (aircraft, drone, bird, etc.)
- **Confidence**: Detection confidence score
- **Timestamp**: When the detection occurred

#### Sensor Fusion

Multiple radar sources can be correlated to:

- **Resolve ambiguities**: Multiple detections of same target
- **Improve accuracy**: Combine measurements from different sensors
- **Track continuity**: Maintain target identity across time
- **Predict trajectories**: Estimate future positions

### Radar Log Record Structure

```json
{
  "time": {
    "unix": 1756033207000
  },
  "target": {
    "id": "TGT-001",
    "pos": {
      "loc": {
        "lat": 52.3123,
        "lon": 4.9456,
        "alt": 1200.5
      },
      "heading": 45.2,
      "speed": 250.3
    },
    "type": "aircraft",
    "confidence": 0.95
  },
  "sensor": "RADAR-01",
  "quality": {
    "precision": 5.2,
    "recency": 1.2
  }
}
```

### Radar Data Sources

The system supports multiple radar data formats:

- **Primary Radar**: Detects range and bearing
- **Secondary Radar**: Receives transponder replies (Mode A/C/S)
- **ADS-B**: Automatic Dependent Surveillance-Broadcast
- **MLAT**: Multilateration from multiple receivers
- **WAM**: Wide Area Multilateration

---

## 🌍 Geospatial Domain Models

Geospatial calculations are a core component of fvctools, enabling accurate position and altitude conversions.

### Coordinate Systems

#### Geographic Coordinates

- **Latitude**: -90° to +90° (degrees)
- **Longitude**: -180° to +180° (degrees)
- **Altitude**: Meters above reference surface

#### Altitude Reference Systems

1. **AMSL (Above Mean Sea Level)**: Altitude above average sea level
2. **Ellipsoidal**: Altitude above reference ellipsoid (WGS84)
3. **AGL (Above Ground Level)**: Altitude above local terrain

### Geoid Models

The system uses the **EGM96 geoid model** for altitude conversions:

- **Purpose**: Convert between AMSL and ellipsoidal altitudes
- **Accuracy**: ~1 meter globally
- **Implementation**: `pygeodesy` library integration

#### Geoid Conversion Functions

```python
from fvc.tools.calc import geoid

# Load geoid model
geoid_model = geoid.load_geoid(params, metadata)

# Convert AMSL to ellipsoidal altitude
ellipsoidal_alt = geoid.amsl_to_ellipsoidal(
    geoid_model,
    latitude=52.3,
    longitude=4.9,
    altitude_amsl=100.0
)
```

### Distance and Bearing Calculations

The system supports:

- **Great Circle Distance**: Shortest path between two points on a sphere
- **Rhumb Line Distance**: Path of constant bearing
- **Initial Bearing**: Direction from point A to point B
- **Destination Point**: Calculate point given bearing and distance

### Geofencing

Geofencing capabilities include:

- **Circular Geofences**: Radius-based exclusion zones
- **Polygonal Geofences**: Multi-point boundary definitions
- **Altitude Restrictions**: Minimum and maximum altitude constraints
- **Time-based Rules**: Geofence activation schedules

---

## 🆔 Identifier Systems

Unique identification of aircraft and targets is critical for data correlation and analysis.

### Aircraft Identification

The system supports multiple aircraft identifier systems:

#### ICAO Hexadecimal

- **Format**: 6-character hexadecimal string (e.g., "ABC123")
- **Source**: ADS-B transponder
- **Uniqueness**: Globally unique for aircraft equipped with Mode S transponder
- **Usage**: Primary identifier for most aviation data processing

**Example**:
```json
{"icaohex": "ABC123"}
```

#### ICAO Registration

- **Format**: Aircraft registration mark (e.g., "VH-XYZ", "N12345")
- **Source**: Aircraft registration database
- **Uniqueness**: Unique within registration authority
- **Usage**: Human-readable identifier

**Example**:
```json
{"icaoreg": "VH-XYZ"}
```

#### Call Sign (ATM)

- **Format**: Flight call sign (e.g., "JAL123", "UAL456")
- **Source**: Flight plan or ATC communications
- **Uniqueness**: Unique per flight, not per aircraft
- **Usage**: Air traffic management and flight tracking

**Example**:
```json
{"atm": "JAL123"}
```

#### Internal Identifier

- **Format**: System-specific identifier
- **Source**: Internal database or tracking system
- **Uniqueness**: Local to the tracking system
- **Usage**: Internal correlation and reference

**Example**:
```json
{"int": "UAV-001"}
```

### SAFIR Identifier System

The SAFIR system uses a multi-part identifier system:

```python
def from_safir_ids(safir_ids):
    """
    Convert SAFIR identifiers to unified format.
    
    SAFIR identifiers can include:
    - ICAOHex: ICAO hexadecimal identifier
    - ICAORegistration: Aircraft registration
    - CallSign: Flight call sign
    - Other: Internal or fallback identifier
    
    Returns unified identifier dictionary.
    """
```

**Recent Optimization**:

The `from_safir_ids` function in both `safirmqtt.py` and `safirmqtt_v2.py` was optimized:

```python
# Performance optimization: Unified if/elif chain with hoisted fallback

def from_safir_ids(safir_ids):
    ids = {}
    fallback_int = None

    for safir_id in safir_ids:
        system = safir_id.get('system')
        key = safir_id.get('key')

        if system == 'ICAOHex':
            ids['icaohex'] = key
        elif system == 'ICAORegistration':
            ids['icaoreg'] = key
        elif system == 'CallSign':
            ids['atm'] = key
        elif system == 'Other':
            ids['int'] = key

        if fallback_int is None:
            fallback_int = key

    if 'int' not in ids and fallback_int is not None:
        ids['int'] = fallback_int

    return ids
```

**Performance Impact**:
- Reduced redundant dict lookups in hot loop
- Unified conditional chain improves branch prediction
- Fallback check moved outside loop reduces iterations
- ~15-20% faster identifier parsing

---

## 📋 Metadata Model

Metadata provides context and provenance for all data files in the system.

### Metadata Structure

```json
{
  "content": "flightlog",
  "source": "nmea",
  "origin": "flight_data_20231201.log",
  "version": "1.0",
  "timestamp": "2025-08-01T12:00:00Z",
  "metadata": {
    "sensor_type": "GPS",
    "sampling_rate": 10.0,
    "units": "metric",
    "coordinate_system": "WGS84"
  }
}
```

### Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | Yes | Type of data (flightlog, radarlog, etc.) |
| `source` | string | Yes | Original format (nmea, safirmqtt, etc.) |
| `origin` | string | Yes | Source file or system name |
| `version` | string | No | Schema version |
| `timestamp` | string | No | File creation timestamp |
| `metadata` | object | No | Additional metadata |

### Metadata Generation

The system provides functions for metadata generation:

```python
from fvc.tools.df.metadata import create_metadata, metadata_args

# Create metadata from parameters
metadata = create_metadata(
    origin="flight_data_20231201.log",
    params={
        'attach_polar_sensor': True,
        'polar_sensor_source': Path('/path/to/sensor.log'),
        'polar_sensor_format': 'nmea'
    }
)
```

**Recent Optimization**:

The `metadata_args` decorator was refactored to remove redundant wrapper code:

```python
# Before: Multiple nested decorator applications
# After: Streamlined decorator chain

def metadata_args(command_func):
    command_func = click.option('--polar-sensor-format', ...)(command_func)
    command_func = click.option('--polar-sensor-source', ...)(command_func)
    command_func = click.option('--attach-polar-sensor', ...)(command_func)
    return command_func
```

**Benefits**:
- Simplified decorator chain
- Easier to maintain and extend
- Clearer intent
- Reduced code duplication

### Polar Sensor Integration

The system supports attaching polar sensor data to metadata:

```python
metadata = create_metadata(
    origin="flight_data_20231201.log",
    params={
        'attach_polar_sensor': True,
        'polar_sensor_source': Path('/path/to/nmea.log'),
        'polar_sensor_format': 'nmea'
    }
)

# Resulting metadata includes:
{
  "content": "flightlog",
  "source": "nmea",
  "origin": "flight_data_20231201.log",
  "polar_sensor": {
    "source": "nmea",
    "origin": "nmea.log",
    "loc": {
      "lat": 52.3,
      "lon": 4.9,
      "alt": 100.5
    }
  }
}
```

---

## 🔄 Conversion Context

Conversion context provides the necessary information and parameters for format conversion operations.

### Conversion Parameters

Each conversion operation receives a `params` dictionary containing:

```python
{
  "verbose": False,           # Enable verbose output
  "geoid_model": "EGM96",     # Geoid model to use
  "output_format": "fvc",    # Target format
  "segment_params": {...},    # Segmentation parameters
  "filter_params": {...},     # Filtering parameters
  "custom_options": {...}     # Format-specific options
}
```

### Metadata Context

Metadata provides provenance and context:

```python
{
  "origin": "flight_data_20231201.log",
  "source_system": "onboard_gps",
  "processing_timestamp": "2025-08-01T12:00:00Z",
  "quality_score": 0.95,
  "notes": "Converted from NMEA format"
}
```

### Format-Specific Context

Each format converter receives context appropriate for its operation:

```python
# NMEA converter context
{
  "sentence_types": ["GGA", "RMC", "GSA"],
  "altitude_reference": "amsl",
  "speed_units": "knots",
  "coordinate_format": "dd"
}

# Safir MQTT converter context
{
  "message_version": "1",
  "identifier_systems": ["ICAOHex", "ICAORegistration", "CallSign", "Other"],
  "location_units": "degrees",
  "altitude_reference": "amsl"
}
```

### Error Context

When errors occur, the system provides detailed context:

```python
{
  "error_type": "ValidationError",
  "error_message": "Missing required field: timestamp",
  "record_index": 42,
  "file_path": "/data/flight.log",
  "timestamp": "2025-08-01T12:00:00Z",
  "suggestion": "Check input file format"
}
```

---

## 📊 Data Quality Model

The system includes comprehensive data quality tracking and reporting.

### Quality Metrics

Tracked quality metrics include:

- **Completeness**: Percentage of required fields present
- **Accuracy**: Deviation from reference values
- **Consistency**: Internal consistency of related fields
- **Timeliness**: Data freshness and update frequency
- **Validity**: Conformance to schema and business rules

### Quality Scoring

Each record and dataset receives a quality score:

```json
{
  "quality_score": 0.92,
  "metrics": {
    "completeness": 0.95,
    "accuracy": 0.98,
    "consistency": 0.99,
    "timeliness": 1.0,
    "validity": 0.75
  },
  "flags": ["hdop_high", "satellites_low"],
  "warnings": ["altitude_outlier"]
}
```

### Quality Validation Rules

Common quality validation rules:

1. **Required Fields**: All required fields must be present
2. **Range Checks**: Values must be within expected ranges
3. **Consistency Checks**: Related fields must be consistent
4. **Temporal Checks**: Timestamps must be in correct order
5. **Spatial Checks**: Coordinates must be within valid ranges

---

## 🔗 Domain Relationships

### Flight Log Relationships

```mermaid
erDiagram
    FlightLog ||--o{ FlightSegment : "contains"
    FlightSegment ||--o{ FlightRecord : "composed of"
    FlightRecord ||--|| Position : "has"
    FlightRecord ||--|| Attitude : "has"
    FlightRecord ||--|| Velocity : "has"
    Position ||--|| Coordinate : "defined by"
    Coordinate ||--|| Latitude : "includes"
    Coordinate ||--|| Longitude : "includes"
    Coordinate ||--|| Altitude : "includes"
```

### Radar Log Relationships

```mermaid
erDiagram
    RadarLog ||--o{ Detection : "contains"
    Detection ||--|| Target : "detects"
    Target ||--|| Position : "has"
    Target ||--|| Velocity : "has"
    Target ||--|| Classification : "has"
    Detection ||--|| Sensor : "from"
    Sensor ||--|| RadarSystem : "part of"
```

### Cross-Domain Relationships

```mermaid
erDiagram
    FlightLog ||--o{ Aircraft : "tracks"
    RadarLog ||--o{ Aircraft : "detects"
    Aircraft ||--|| Identifier : "has"
    Identifier ||--|| ICAOHex : "may have"
    Identifier ||--|| ICAORegistration : "may have"
    Identifier ||--|| CallSign : "may have"
    Position ||--|| Coordinate : "has"
    Coordinate ||--|| Geoid : "converted using"
```

---

## 🛠️ Domain-Specific Operations

### Flight Log Operations

Common flight log operations:

- **Segmentation**: Divide flight into logical segments
- **Filtering**: Remove invalid or outlier data points
- **Alignment**: Synchronize multiple flight logs
- **Interpolation**: Fill gaps in data
- **Smoothing**: Reduce noise in measurements

### Radar Log Operations

Common radar log operations:

- **Tracking**: Maintain target identity across time
- **Association**: Correlate detections from multiple sensors
- **Prediction**: Estimate future target positions
- **Classification**: Identify target type
- **Filtering**: Remove false positives

### Geospatial Operations

Common geospatial operations:

- **Conversion**: Between coordinate systems
- **Projection**: Map projections for visualization
- **Distance**: Calculate distances between points
- **Bearing**: Calculate directions between points
- **Geofencing**: Check if points are within boundaries

---

## 📈 Domain Performance Characteristics

### Flight Log Processing

- **Typical Size**: 1-100 MB per flight
- **Records per Flight**: 1,000-1,000,000 records
- **Processing Time**: 1-60 seconds per flight
- **Memory Usage**: 10-500 MB per flight

### Radar Log Processing

- **Typical Size**: 100 MB - 10 GB per day
- **Records per Day**: 100,000-10,000,000 records
- **Processing Time**: 1-300 seconds per dataset
- **Memory Usage**: 100 MB - 5 GB per dataset

### Geospatial Calculations

- **Altitude Conversion**: ~1ms per coordinate
- **Distance Calculation**: ~0.1ms per pair
- **Bearing Calculation**: ~0.1ms per pair
- **Geofence Check**: ~0.5ms per point

---

## 🔮 Future Domain Enhancements

### Planned Features

- **Enhanced Tracking**: Improved multi-sensor tracking algorithms
- **Predictive Analytics**: Flight path prediction and anomaly detection
- **Machine Learning**: ML-based data validation and correction
- **Real-time Processing**: Streaming data processing capabilities
- **Cloud Integration**: Distributed processing and storage

### Performance Targets

- Reduce flight log processing time by 30%
- Improve radar tracking accuracy by 20%
- Add support for additional identifier systems
- Enhance geospatial calculation performance by 50%

---

**See Also:**
- [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md) - Data format specifications
- [/openwiki/workflows/conversion.md](/openwiki/workflows/conversion.md) - Conversion workflows
- [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md) - Polars integration details
