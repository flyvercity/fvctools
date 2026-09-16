---
type: Architecture Guide
title: Architecture Overview

description: High-level system architecture of fvctools including components, data flow, design principles, and integration points for the CLI suite and .fvc format

tags: [architecture, design, components, patterns, cli, data-format]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T12:24:16.401Z
sources:
  - id: openwiki-source-d89fcd3fc5cba86004bd8f31
    resource: repo://src/fvc/tools/cli.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T12:24:16.401Z" }
---

# Architecture Overview

This guide provides a comprehensive overview of the **fvctools** architecture, including components, design patterns, data flow, and integration points.

## Overview

fvctools is a **modular Python-based CLI suite** designed for processing, converting, and validating geospatial aviation data. It serves as the backbone of Flyvercity's data pipeline, enabling seamless data integration and analysis across different platforms and formats.

## Architecture Principles

### 1. Modular Design

fvctools follows **modular architecture** principles:

- ✅ **Separation of concerns**: Each module has a single responsibility
- ✅ **Loose coupling**: Modules interact through well-defined interfaces
- ✅ **High cohesion**: Related functionality is grouped together
- ✅ **Reusability**: Components can be reused across the codebase
- ✅ **Extensibility**: Easy to add new formats and features

### 2. CLI-Centric

The primary interface is the **command-line interface (CLI)**:

- ✅ **Click framework**: Modern CLI framework with help generation
- ✅ **Subcommands**: Organized by toolset (df, calc, render, flightlog)
- ✅ **Consistent interface**: Uniform argument parsing and error handling
- ✅ **Scriptable**: Easy to integrate into larger workflows
- ✅ **Rich logging**: Colorized, structured logging with Rich

### 3. Data-Centric

All operations revolve around the **Flyvercity Data Format (.fvc)**:

- ✅ **Unified format**: Single format for all aviation data
- ✅ **JSON-Lines**: Human-readable and machine-processable
- ✅ **Schema validation**: Strict validation against schemas
- ✅ **Metadata-first**: METADATA record describes file content
- ✅ **Content types**: Support for flightlog, radarlog, and other content types

### 4. Performance-Optimized

Recent commits show a focus on **performance optimizations**:

- ✅ **Polars integration**: High-performance DataFrame operations
- ✅ **Lazy evaluation**: Memory-efficient processing
- ✅ **Parallel processing**: Multi-core utilization
- ✅ **Streaming where possible**: Process large files efficiently
- ✅ **Optimized validation**: Pre-compiled JSON schema validators

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                        fvctools CLI (Click-based)                            │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┬───────┤
│    fvc df       │   fvc calc      │  fvc render     │ fvc flightlog   │ fvc   │
│  (Data File)    │ (Calculations)  │ (Visualization) │ (Flight Analysis)│ tools │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  /src/fvc/tools/│ │ /src/fvc/   │ │ /src/fvc/tools/ │ │ /src/fvc/tools/ │
│      df/        │ │   calc/     │ │    render/      │ │ flightlog/      │
└────────┬────────┘ └──────┬──────┘ └───────┬─────────┘ └────────┬────────┘
         │                 │                │                  │
         ▼                 ▼                ▼                  ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     Core Libraries & Shared Components                       │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┬───────┤
│  Conversion     │  Validation     │  Visualization  │  Geospatial     │ Shared│
│  Engine         │  Engine         │  Engine         │  Calculations   │ Utils │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     Data Format (.fvc) - JSON-Lines                           │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────┐    ┌─────────┐  │
│  │  METADATA   │    │  FLIGHTLOG  │    │    RADARLOG       │    │  ...    │  │
│  │  Record     │    │  Record     │    │    Record         │    │         │  │
│  └─────────────┘    └─────────────┘    └───────────────────┘    └─────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. CLI Layer

**Location**: `/src/fvc/tools/cli.py`

**Responsibilities**:
- Parse command-line arguments using Click framework
- Route to appropriate toolset (df, calc, render, flightlog)
- Handle global options (verbose, JSON output, AWS profile, EGM geoid data)
- Configure logging and error handling
- Provide shell integration utilities

**Key Components**:

```python
# /src/fvc/tools/cli.py

import click
from fvc.tools.df.cli import df
from fvc.tools.calc.cli import calc
from fvc.tools.render.cli import render
from fvc.tools.flightlog.cli import flightlog_group

@click.group(help='Flyvercity CLI Tools Suite')
@click.version_option(version('fvctools'))
@click.option('--verbose', is_flag=True, help='sets logging level to debug')
@click.option('--json', is_flag=True, help='Make JSON default output format')
@click.option('--no-pprint', is_flag=True, help='Disable colored pretty printing')
@click.option('--aws-profile', help='AWS profile to use for S3 operations')
@click.option('--egm', type=click.Path(exists=True), help='Custom EGM geoid data file')
def cli(ctx, verbose, json, no_pprint, aws_profile, egm):
    """Main CLI entry point with global configuration"""
    # Configure logging with Rich handler
    # Set up context object with configuration
    pass

cli.add_command(df)
cli.add_command(calc)
cli.add_command(render)
cli.add_command(flightlog_group)
```

### 2. Toolset Layer

Four main toolsets:

#### a) Data File Tools (`fvc df`)

**Location**: `/src/fvc/tools/df/`

**Responsibilities**:
- Convert external formats to .fvc
- Validate .fvc files
- Correlate multiple data sources
- Manage data fusion operations
- Export from .fvc to external formats

**Submodules**:

```
src/fvc/tools/df/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands (validate, convert, export, help)
├── core.py                  # Conversion and validation engine
├── correlate.py             # Correlation engine
├── fusion.py                # Fusion operations
├── metadata.py              # METADATA handling utilities
├── schema.py                # Schema validation utilities
├── schema.yaml              # JSON Schema definitions
├── utils.py                 # Utility functions
└── xformats/                # Format converters (30+ formats)
    ├── __init__.py
    ├── base.py              # Base converter class (no longer used directly)
    ├── nmea.py              # NMEA converter
    ├── ulog.py              # ULog converter
    ├── safirmqtt.py         # SAFIR MQTT converter
    ├── safirmqtt_v2.py      # Optimized SAFIR MQTT converter
    ├── datcon.py            # DatCon converter
    ├── senhive.py           # SenHive converter
    ├── agentfly.py          # AgentFly converter
    ├── geojson.py           # GeoJSON converter
    ├── kml/                 # KML format support
    ├── artlog.py            # ART log format
    ├── courageous.py        # Courageous flight logs
    ├── csgroup.py           # CS Group radar/tracking logs
    ├── gnettrack.py         # G-NetTrack GPS logs
    ├── manna.py             # Manna flight logs
    ├── robinradar.py        # Robin Radar system logs
    └── ...                  # 15+ additional formats
```

**Key Functions**:

```python
# /src/fvc/tools/df/core.py

def convert(
    params: DFParams,
    callback: Callable[[int], None] | None = None
):
    """
    Convert a file from an external format to FVC format.
    
    Uses importlib to dynamically load the appropriate converter module
    and calls convert_to_fvc() function from that module.
    """
    # Validates input/output paths are different
    # Imports the converter module dynamically
    # Creates metadata
    # Uses JsonlinesIO context manager for file I/O
    # Calls converter function with params, metadata, input_path, and IO object

def validate(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
    """
    Validate a .fvc file against the schema.
    
    Uses pre-compiled JSON schema validators for performance.
    Tracks error count and stops after MAX_ERRORS (100) to avoid flooding logs.
    """
    # Reads metadata line first
    # Validates against METADATA schema
    # For each data record, validates against content-specific schema
    # Returns True if no errors, False otherwise
```

**Example Converter Module**:

```python
# /src/fvc/tools/df/xformats/nmea.py

def convert_to_fvc(params, meta, input_path, io):
    """
    Convert NMEA format to .fvc format.
    
    This is the entry point called by the conversion engine.
    """
    # Parse NMEA sentences
    # Convert to flightlog records
    # Write to output using JsonlinesIO
    pass

def export_from_fvc(params, output_path):
    """
    Export from .fvc to external format.
    """
    # Read .fvc file
    # Transform data
    # Write to output format
    pass
```

#### b) Geospatial Calculations (`fvc calc`)

**Location**: `/src/fvc/tools/calc/`

**Responsibilities**:
- Geoid undulation calculations (EGM96/EGM2008)
- Terrain elevation lookups from DEM files
- Coordinate transformations
- Geospatial calculations for aviation data

**Submodules**:

```
src/fvc/tools/calc/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands
├── geoid.py                 # Geoid calculations (EGM models)
├── terrain.py               # Terrain calculations (DEM access)
└── utils.py                 # Utility functions
```

**Key Functions**:

```python
# /src/fvc/tools/calc/geoid.py

def get_undulation(lat: float, lon: float, egm_file: str = None) -> float:
    """Get EGM geoid undulation at given coordinates"""
    from pygeodesy import EGM96, EGM2008
    # Uses EGM96 by default, can use custom EGM file
    geoid = EGM96() if egm_file is None else EGM96(egm_file)
    return geoid.height(lat, lon)

def altitude_to_amsl(altitude: float, lat: float, lon: float, egm_file: str = None) -> float:
    """Convert ellipsoidal altitude to AMSL"""
    undulation = get_undulation(lat, lon, egm_file)
    return altitude - undulation

# /src/fvc/tools/calc/terrain.py

def get_terrain_elevation(lat: float, lon: float, dem_path: str = None) -> float:
    """Get terrain elevation at given coordinates from DEM file"""
    import rasterio
    # Opens DEM file and samples elevation at (lat, lon)
    # Supports custom DEM paths or default locations
```

#### c) Visualization (`fvc render`)

**Location**: `/src/fvc/tools/render/`

**Responsibilities**:
- Generate interactive maps
- Create flight path visualizations
- Export to multiple formats (HTML, KML, JSON)
- Template-based rendering with Jinja2
- 3D visualization support

**Submodules**:

```
src/fvc/tools/render/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands
├── core.py                  # Rendering engine
├── templates.py             # Template management and rendering
└── templates/               # Jinja2 templates
    ├── flight_map.html
    ├── index.html
    ├── flight_map_3d.html
    └── ...
```

**Key Classes**:

```python
# /src/fvc/tools/render/core.py

class RenderEngine:
    """Core rendering engine"""
    
    def render_flight(self, input_path: str, output_dir: str, **options):
        """Render flight data visualization"""
        # Load .fvc file
        # Process data into flight path
        # Render template with flight data
        # Write output files
        pass
    
    def _get_template(self, name: str):
        """Get Jinja2 template"""
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader("templates/"))
        return env.get_template(name)

# /src/fvc/tools/render/templates.py

def render_template(template_name: str, context: dict, output_path: str):
    """Render a template with context to output file"""
    # Uses Jinja2 to render template
    # Supports multiple output formats
```

#### d) Flight Log Analysis (`fvc flightlog`)

**Location**: `/src/fvc/tools/flightlog/`

**Responsibilities**:
- Flight log segmentation and analysis
- Flight statistics calculation
- Flight log splitting and merging
- Waypoint extraction
- Flight phase detection

**Submodules**:

```
src/fvc/tools/flightlog/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands
├── load.py                  # Flight log loading utilities
├── segment.py               # Flight segmentation logic
├── split.py                 # Flight log splitting
└── stats.py                 # Flight statistics calculation
```

**Key Features**:

```python
# Flight segmentation based on takeoff/landing detection
# Waypoint extraction from flight paths
# Flight statistics (duration, distance, max altitude, etc.)
# Flight phase classification (taxi, takeoff, cruise, landing)
```

### 3. Core Libraries

#### a) Format Converters

**Location**: `/src/fvc/tools/df/xformats/`

**Responsibilities**:
- Convert external formats to .fvc
- Parse format-specific data structures
- Transform to unified schema
- Handle format-specific edge cases
- Export from .fvc to external formats

**Converter Interface**:

All converters implement two functions:

```python
def convert_to_fvc(params, meta, input_path, io):
    """
    Convert external format to .fvc
    
    Args:
        params: Conversion parameters
        meta: Metadata dictionary
        input_path: Path to input file
        io: JsonlinesIO object for output
    """
    pass

def export_from_fvc(params, output_path):
    """
    Export from .fvc to external format
    
    Args:
        params: Export parameters
        output_path: Path to output file
    
    Returns:
        Path to actual output file (may differ from requested)
    """
    pass
```

**Format Support**:

| Format | Module | Description |
|--------|--------|-------------|
| **NMEA** | `nmea.py` | Standard GPS protocol |
| **ULog** | `ulog.py` | PX4 flight controller logs |
| **SAFIR MQTT** | `safirmqtt.py`, `safirmqtt_v2.py` | Telemetry streaming (v2 optimized) |
| **DatCon** | `datcon.py` | Flight recorder format (ArduPilot) |
| **SenHive** | `senhive.py` | Flight logging system |
| **AgentFly** | `agentfly.py` | Simulator logs |
| **DJI** | `dji.py` | DJI drone data |
| **GeoJSON** | `geojson.py` | Geographic features |
| **KML** | `kml/` | Google Earth format |
| **ART** | `artlog.py` | ART log format |
| **Courageous** | `courageous.py` | Research flight logs |
| **CS Group** | `csgroup.py` | Radar and tracking logs |
| **G-NetTrack** | `gnettrack.py` | GPS track logs |
| **Manna** | `manna.py` | Manna flight logs |
| **Robin Radar** | `robinradar.py` | Radar system logs |
| **Additional formats** | Various | 15+ more aviation data formats |

**Example: Polars-Optimized Converter**

```python
# /src/fvc/tools/df/xformats/agentfly.py

import polars as pl

def convert_to_fvc(params, meta, input_path, io):
    """Convert AgentFly CSV to .fvc using Polars for performance"""
    
    # Read with Polars (lazy evaluation)
    df = pl.scan_csv(input_path)
    
    # Transform with Polars operations
    df = (df
        .with_columns(
            pl.col("timestamp").cast(pl.Int64),
            pl.col("latitude").cast(pl.Float64),
            pl.col("longitude").cast(pl.Float32),  # Float32 for coordinates
            pl.col("altitude").cast(pl.Float32),
        )
        .filter(pl.col("timestamp").is_not_null())
    )
    
    # Write METADATA
    io.write_metadata(meta)
    
    # Iterate through DataFrame and write records
    for row in df.collect().iter_rows(named=True):
        record = {
            "time": {"unix": row["timestamp"]},
            "pos": {
                "loc": {
                    "lat": row["latitude"],
                    "lon": row["longitude"],
                    "alt": row["altitude"],
                }
            }
        }
        io.write_record(record)
```

#### b) Schema Validation

**Location**: `/src/fvc/tools/df/schema.py` and `/src/fvc/tools/df/schema.yaml`

**Responsibilities**:
- Validate .fvc files against schemas
- Check METADATA structure
- Validate data records against content-specific schemas
- Provide detailed error messages
- Support multiple content types

**Schema Structure**:

```yaml
# /src/fvc/tools/df/schema.yaml

METADATA:
  type: object
  properties:
    content:
      type: string
      enum: [flightlog, radarlog, fusion.replay, capture.message, ...]
    source:
      type: string
      description: Source format
    origin:
      type: string
      description: Original file name
  required: [content, source, origin]
  additionalProperties: false

CONTENT_SCHEMA:
  flightlog:
    $ref: "#/$defs/FLIGHTLOG"
  radarlog:
    $ref: "#/$defs/RADARLOG"
  # ... other content types

FLIGHTLOG:
  type: object
  properties:
    time:
      type: object
      properties:
        unix:
          type: integer
          description: Unix timestamp in milliseconds
    pos:
      type: object
      properties:
        loc:
          $ref: "#/$defs/LOCATION"
    # ... other flightlog fields
```

**Validation Process**:

```python
# /src/fvc/tools/df/core.py

def validate(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
    with dfu.JsonlinesIO(input_path, 'r', callback=callback, raw=True) as f:
        # Validate METADATA
        metaline = f.read()
        jsonschema.validate(metaline, schema.METADATA)
        content = metaline['content']
        
        # Get content-specific schema
        content_schema = schema.CONTENT_SCHEMA[content]
        
        # Pre-compile validator for performance
        cls = jsonschema.validators.validator_for(content_schema)
        validator = cls(content_schema)
        
        # Validate each data record
        for data in f.iterate():
            try:
                validator.validate(data)
            except Exception as e:
                lg.error(f'Validation error at line {f.in_line_no()}: {e}')
                error_count += 1
```

#### c) Metadata Handling

**Location**: `/src/fvc/tools/df/metadata.py`

**Responsibilities**:
- Parse METADATA records
- Validate METADATA structure
- Extract metadata fields
- Generate METADATA for output files
- Provide metadata utilities

**Metadata Utilities**:

```python
# /src/fvc/tools/df/metadata.py

def create_metadata(source_name: str, params: dict) -> dict:
    """Create METADATA record for output file"""
    return {
        "content": params.get('target', 'flightlog'),
        "source": source_name,
        "origin": str(params.get('input_path', 'unknown')),
        "created": datetime.utcnow().isoformat() + 'Z',
        "version": "1.0",
    }
```

### 4. Data Format (.fvc)

**The Flyvercity Data Format** is the unified format used by all tools.

**Format**: JSON-Lines (`.jsonl`)

**Structure**:

```
Line 1: METADATA record (JSON object)
Line 2+: Data records (FLIGHTLOG, RADARLOG, etc.) (JSON objects)
```

**Example**:

```json
{"content": "flightlog", "source": "nmea", "origin": "flight.log", "created": "2024-01-15T10:30:00Z", "version": "1.0"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}}
{"time": {"unix": 1756033206883}, "pos": {"loc": {"lat": 52.3001, "lon": 4.9001, "alt": 100.8}}}
```

**Schema**: Defined in `/src/fvc/tools/df/schema.yaml`

**Content Types**:

| Content Type | Record Type | Description |
|--------------|-------------|-------------|
| `flightlog` | FLIGHTLOG | Flight log entry |
| `radarlog` | RADARLOG | Radar log entry |
| `fusion.replay` | FUSION_REPLAY | Fusion engine replay |
| `capture.message` | CAPTURE_MESSAGE | MQTT message capture |
| `geojson.feature` | GEOJSON_FEATURE | GeoJSON feature collection |
| `kml.features` | KML_FEATURES | KML features |
| ... | ... | ... (extensible) |

**Schema Location**: `/src/fvc/tools/df/schema.yaml` (537 lines with detailed field definitions)

## Integration Points

### 1. External Libraries

fvctools integrates with several external libraries:

| Library | Purpose | Integration |
|---------|---------|-------------|
| **Polars** | High-performance DataFrames | Format converters (agentfly, datcon, senhive, safirmqtt_v2) |
| **PyGeodesy** | Geodetic calculations | Calculation tools (EGM models) |
| **GeoPandas** | Geospatial data manipulation | Visualization and analysis |
| **Rasterio** | DEM access | Terrain calculations |
| **PyNMEA2** | NMEA parsing | NMEA converter |
| **PyULog** | ULog parsing | ULog converter |
| **SimpleKML** | KML generation | Visualization export |
| **Jinja2** | HTML templating | Visualization rendering |
| **Click** | CLI framework | Main CLI interface |
| **JSONSchema** | Schema validation | .fvc file validation |
| **Rich** | Colorized logging | Enhanced user experience |
| **Boto3** | AWS S3 integration | Cloud storage support |
| **Benedict** | Dictionary utilities | Configuration management |
| **Python-dateutil** | Date/time parsing | Temporal data handling |

### 2. External Formats

fvctools supports conversion from multiple external formats:

**Drone/Autopilot Logs**:
- NMEA (GPS protocol)
- ULog (PX4 flight controller)
- DatCon (ArduPilot flight recorder)
- SenHive (Flight logging system)
- AgentFly (Simulator logs)
- DJI (DJI drone data)
- Courageous (Research flight logs)
- Manna (Manna flight logs)

**Radar/Tracking Systems**:
- SAFIR MQTT (Telemetry streaming)
- CS Group (Radar and tracking logs)
- Robin Radar (Radar system logs)

**Geospatial Formats**:
- GeoJSON (Geographic features)
- KML (Google Earth format)
- G-NetTrack (GPS track logs)

**Additional Formats**:
- ART logs
- And 15+ more aviation data formats

### 3. Output Formats

fvctools can export to multiple formats:

| Format | Tool | Description |
|--------|------|-------------|
| **.fvc** | All | Unified Flyvercity Data Format (JSON-Lines) |
| **HTML** | `fvc render` | Interactive maps and visualizations |
| **KML** | `fvc render` | Google Earth format |
| **JSON** | `fvc render` | Data export |
| **CSV** | `fvc df export` | Comma-separated values |
| **GeoJSON** | `fvc df export` | Geographic JSON features |

### 4. CLI Integration

All toolsets integrate through the main CLI:

```bash
# Data File Tools
fvc df --in input.nmea convert nmea output.fvc
fvc df --in output.fvc validate
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc
fvc df --in input.fvc export geojson output.geojson

# Geospatial Calculations
fvc calc undulation 52.3 4.9
fvc calc terrain 52.3 4.9 100.0 --dem /path/to/dem.tif

# Visualization
fvc render flight flight.fvc --output ./map
fvc render flight flight.fvc --template flight_map_3d.html --output ./map3d

# Flight Log Analysis
fvc flightlog stats flight.fvc
fvc flightlog segment flight.fvc --output segmented/
```

## Performance Considerations

### 1. Polars Integration

Heavy use of **Polars** for performance-critical operations:

**Benefits**:
- ✅ **Blazing-fast operations**: Rust-based implementation
- ✅ **Lazy evaluation**: Memory-efficient processing
- ✅ **Parallel processing**: Multi-core utilization
- ✅ **Columnar storage**: Efficient memory usage
- ✅ **Lazy API**: Build query plan before execution

**Converters using Polars**:
- `agentfly.py` - AgentFly CSV converter
- `datcon.py` - DatCon converter
- `senhive.py` - SenHive converter
- `safirmqtt_v2.py` - Optimized SAFIR MQTT converter

**Example**:

```python
# /src/fvc/tools/df/xformats/agentfly.py

def convert_to_fvc(params, meta, input_path, io):
    # Read with Polars (lazy evaluation)
    df = pl.scan_csv(input_path)
    
    # Transform with Polars
    df = (df
        .with_columns(
            pl.col("timestamp").cast(pl.Int64),
            pl.col("latitude").cast(pl.Float64),
            pl.col("longitude").cast(pl.Float32),  # Float32 for coordinates
        )
        .filter(pl.col("timestamp").is_not_null())
    )
    
    # Materialize and iterate
    for row in df.collect().iter_rows(named=True):
        # Write record to .fvc
        pass
```

### 2. Streaming Processing

For large files, use **streaming processing**:

```python
# Process large files line by line
with open("large_file.jsonl", "r") as f:
    for line in f:
        record = json.loads(line)
        process_record(record)
```

The `JsonlinesIO` context manager in `/src/fvc/tools/df/utils.py` provides optimized streaming I/O with progress tracking.

### 3. Memory Management

**Techniques**:

- ✅ **Use appropriate data types**: `Float32` instead of `Float64` for coordinates
- ✅ **Lazy evaluation**: Process data without materializing
- ✅ **Chunk processing**: Process in manageable chunks
- ✅ **Close files**: Use context managers
- ✅ **Pre-compiled validators**: Avoid recompiling JSON schema for each record

**Example**:

```python
# ✅ Good: Use Float32 for coordinates (4 bytes vs 8 bytes for Float64)
pl.Float32()

# ✅ Good: Lazy evaluation with Polars
lazy_df = pl.scan_csv(input_path)
result = lazy_df.filter(...).collect()

# ✅ Good: Chunk processing with Polars
chunk_size = 10000
df = pl.scan_csv(input_path)
for chunk in df.iter_slices(chunk_size):
    process_chunk(chunk.collect())
```

### 4. Parallel Processing

**Techniques**:

- ✅ **Polars parallel operations**: Automatic parallelization
- ✅ **GNU parallel**: Parallel processing of multiple files
- ✅ **Multiprocessing**: CPU-bound tasks
- ✅ **ThreadPoolExecutor**: I/O-bound tasks

**Example**:

```python
# Polars automatically parallelizes
result = df.group_by("flight_id").agg(...).collect()

# GNU parallel for batch processing
find ./input -name "*.nmea" | parallel -j $(nproc) fvc df convert nmea {} {.}.fvc

# Multiprocessing for CPU-bound tasks
from multiprocessing import Pool

with Pool() as pool:
    results = pool.map(process_file, file_list)
```

### 5. Optimized Validation

**Performance optimizations**:

```python
# /src/fvc/tools/df/core.py

def validate(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
    # Pre-compile validator once
    cls = jsonschema.validators.validator_for(content_schema)
    cls.check_schema(content_schema)
    validator = cls(content_schema)
    
    # Use validator for all records (faster than recompiling)
    for data in f.iterate():
        validator.validate(data)
```

## Error Handling and Validation

### 1. Schema Validation

**Strict validation** ensures data quality:

```python
# Validation process:
# 1. Validate METADATA record against METADATA schema
# 2. Extract content type
# 3. Get content-specific schema
# 4. Pre-compile validator
# 5. Validate each data record
# 6. Track errors and stop after MAX_ERRORS (100)
```

### 2. Graceful Degradation

**Handle errors without crashing**:

```python
# /src/fvc/tools/df/xformats/nmea.py

def convert_to_fvc(params, meta, input_path, io):
    try:
        # Write METADATA
        io.write_metadata(meta)
        
        # Parse with error handling
        with open(input_path, "r") as f:
            for line in f:
                if line.startswith("$"):
                    try:
                        msg = pynmea2.parse(line)
                        record = convert_nmea_to_record(msg)
                        io.write_record(record)
                    except Exception as e:
                        lg.warning(f"Failed to parse NMEA sentence: {e}")
                        continue
        
        return True
    except Exception as e:
        lg.error(f"Conversion failed: {e}")
        return False
```

### 3. Detailed Error Messages

**Provide actionable error information**:

```python
# Structured error handling with Rich logging
lg.error(f'Validation error at line {f.in_line_no()}: {e}')
lg.warning(f'Failed to parse NMEA sentence: {e}')
lg.info(f'Conversion succeeded: {output_path}')

# Context-rich error messages
try:
    process_file(file_path)
except FileNotFoundError as e:
    lg.error(f"File not found: {file_path}")
    raise FileNotFoundError(f"Input file not found: {file_path}")
except ValidationError as e:
    lg.error(f"Validation failed at line {line_num}: {e.message}")
    raise ValueError(f"Invalid data at line {line_num}: {e.message}")
except Exception as e:
    lg.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

## Security Considerations

### 1. Input Validation

**Validate all inputs**:

```python
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def safe_path(base_dir: str, relative_path: str) -> str:
    """Ensure path is within base directory"""
    full_path = Path(base_dir) / relative_path
    if not full_path.resolve().startswith(Path(base_dir).resolve()):
        raise ValueError("Path traversal detected")
    return str(full_path)

# Used in CLI:
input_path = params.get('input_path')
if not input_path.exists():
    raise UserWarning(f'Input file not found: {input_path}')
```

### 2. File Permissions

**Set appropriate permissions**:

```python
import os

# Set file permissions
os.chmod("output.fvc", 0o644)  # Read/write for owner, read for others

# Use umask
os.umask(0o022)  # Default: 644 for files, 755 for directories

# Run as non-root user (enforced in CLI)
if os.geteuid() == 0:
    raise RuntimeError("Do not run as root")
```

### 3. Credential Management

**Use environment variables**:

```python
import os

# AWS credentials from environment
aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

# Configured via CLI option --aws-profile
# Uses boto3 session configuration

# Custom EGM geoid data
# Configured via CLI option --egm
# Uses custom EGM file for geoid calculations
```

### 4. Path Traversal Protection

**Prevent directory traversal attacks**:

```python
# All file paths are validated before use
# CLI validates input_path.exists()
# Output paths are checked to ensure they're writable
# No arbitrary code execution from file contents
```

## Testing Architecture

### 1. Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Test fixtures
├── test_*.py                # Test files
│   ├── test_nmea_xformat.py
│   ├── test_ulog_xformat.py
│   ├── test_conversion.py
│   ├── test_validation.py
│   ├── test_cli.py
│   ├── test_polars_integration.py
│   └── ...
├── fixtures/                # Test data
│   ├── nmea_samples.py
│   ├── flight_records.py
│   ├── schema_samples.py
│   └── ...
└── utils.py                 # Test utilities
```

### 2. Test Fixtures

**Reusable test setup**:

```python
# tests/conftest.py

import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_nmea():
    """Sample NMEA data"""
    return "$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46"

@pytest.fixture
def sample_fvc_file():
    """Create a sample .fvc file for testing"""
    # Returns Path to temporary .fvc file
    pass
```

### 3. Test Coverage

**Aim for comprehensive coverage**:

```bash
# Run tests with coverage
pytest --cov=src/fvc --cov-report=html

# Set minimum coverage in pyproject.toml
[tool.pytest.ini_options]
addopts = --cov=src/fvc --cov-report=term-missing --cov-fail-under=80
minversion = 6.0
```

**Test categories**:
- Unit tests for individual functions
- Integration tests for converter modules
- Validation tests for schema validation
- CLI tests for command-line interface
- Performance tests for Polars operations
- Error handling tests for edge cases

## Deployment Architecture

### 1. Development Deployment

**Editable install**:

```bash
# Clone repository
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Install in development mode
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### 2. Production Deployment

**Isolated installation**:

```bash
# Create virtual environment
python -m venv /opt/fvctools/.venv
source /opt/fvctools/.venv/bin/activate

# Install production dependencies
cd /opt/fvctools
uv pip install .

# Or with pip
pip install .
```

### 3. Containerized Deployment

**Docker container**:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir uv
RUN uv pip install --no-cache-dir .

# Set environment variables
ENV FVC_DATA_DIR=/data
ENV FVC_LOG_LEVEL=INFO

# Create data directory
RUN mkdir -p /data && chown -R 1000:1000 /data

# Set user
USER 1000

# Command
CMD ["fvc", "--version"]
```

**Docker Compose example**:

```yaml
version: '3.8'

services:
  fvctools:
    build: .
    volumes:
      - ./data:/data
    environment:
      - FVC_LOG_LEVEL=INFO
      - FVC_DATA_DIR=/data
    user: "1000:1000"
```

### 4. Service Deployment

**Systemd service**:

```ini
# /etc/systemd/system/fvctools.service

[Unit]
Description=Flyvercity CLI Tools Service
After=network.target

[Service]
Type=simple
User=fvctools
Group=fvctools
WorkingDirectory=/opt/fvctools
Environment="FVC_DATA_DIR=/var/lib/fvctools"
Environment="FVC_LOG_LEVEL=INFO"
ExecStart=/opt/fvctools/.venv/bin/fvc --version
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Monitoring and Logging

### 1. Logging Architecture

**Structured logging with Rich**:

```python
import logging as lg
from rich.logging import RichHandler

# Configure logging
lg.basicConfig(
    level=lg.DEBUG if verbose else lg.INFO,
    handlers=[RichHandler(rich_tracebacks=verbose, show_path=verbose)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Usage
lg.debug(f'Verbose mode is {"on" if verbose else "off"}')
lg.info(f'Conversion succeeded: {output_path}')
lg.warning(f'Failed to parse NMEA sentence: {e}')
lg.error(f'Validation error at line {line_num}: {e}')
```

**Log levels**:
- DEBUG: Detailed debugging information
- INFO: Normal operation messages
- WARNING: Recoverable issues
- ERROR: Serious problems

### 2. Metrics Collection

**Performance metrics** (future enhancement):

```python
# Example of metrics integration (planned)
from prometheus_client import start_http_server, Counter, Histogram

# Metrics
CONVERSION_COUNT = Counter(
    'fvctools_conversions_total',
    'Total number of conversions',
    ['format']
)

CONVERSION_TIME = Histogram(
    'fvctools_conversion_duration_seconds',
    'Conversion duration in seconds',
    ['format']
)

# Usage
@CONVERSION_TIME.labels(format=fmt).time()
def convert(input_path, output_path, fmt):
    CONVERSION_COUNT.labels(format=fmt).inc()
    # Conversion logic
    ...
```

## Performance Optimization Patterns

### 1. Lazy Evaluation Pattern

```python
import polars as pl

# ✅ Good: Use lazy evaluation
lazy_df = pl.scan_csv(input_path)
result = lazy_df.filter(...).collect()

# ❌ Bad: Eager evaluation (materializes intermediate results)
result = pl.read_csv(input_path).filter(...).collect()
```

### 2. Streaming Pattern

```python
# ✅ Good: Stream large files using JsonlinesIO
with dfu.JsonlinesIO(input_path, 'r') as f:
    for record in f.iterate():
        process_record(record)

# ❌ Bad: Load entire file into memory
data = f.read()  # Large memory usage
```

### 3. Parallel Processing Pattern

```python
# ✅ Good: Use Polars parallel operations
result = df.group_by("flight_id").agg(...).collect()

# ✅ Good: Use GNU parallel for batch processing
find ./input -name "*.nmea" | parallel -j $(nproc) fvc df convert nmea {} {.}.fvc

# ✅ Good: Use multiprocessing for CPU-bound tasks
from multiprocessing import Pool

with Pool() as pool:
    results = pool.map(process_file, file_list)
```

### 4. Caching Pattern

```python
import functools

@functools.lru_cache(maxsize=100)
def get_geoid_undulation(lat: float, lon: float, egm_file: str = None) -> float:
    """Cache geoid undulation calculations"""
    from pygeodesy import EGM96
    geoid = EGM96(egm_file) if egm_file else EGM96()
    return geoid.height(lat, lon)
```

## Evolution and Future Directions

### 1. Recent Changes

Based on repository evidence, recent changes include:

- ✅ **Polars integration** (multiple converters optimized)
- ✅ **Performance optimizations** (lazy evaluation, pre-compiled validators)
- ✅ **Format converter improvements** (30+ formats supported)
- ✅ **Schema validation enhancements** (detailed schema with documentation)
- ✅ **Code refactoring** (cleaner architecture, better separation of concerns)
- ✅ **Rich logging integration** (enhanced user experience)
- ✅ **Flight log analysis tools** (new flightlog toolset)
- ✅ **AWS S3 integration** (cloud storage support)
- ✅ **Custom EGM geoid support** (flexible geoid calculations)

### 2. Future Enhancements

Potential future directions:

1. **Additional format converters**
   - MAVLink support
   - ArduPilot logs
   - Pixhawk logs
   - Litchi logs
   - More radar/tracking systems

2. **Cloud integration**
   - AWS S3 direct access (already partially implemented)
   - Google Cloud Storage
   - Azure Blob Storage
   - Cloud-based processing

3. **Database integration**
   - PostgreSQL spatial support
   - MongoDB for flexible schema
   - TimescaleDB for time-series
   - InfluxDB for metrics

4. **Enhanced visualization**
   - Plotly integration
   - Three.js for 3D
   - D3.js for advanced visualizations
   - Export to multiple formats

5. **Machine learning**
   - Anomaly detection
   - Predictive analytics
   - Pattern recognition
   - Automated quality control

6. **Real-time processing**
   - Kafka integration
   - RabbitMQ support
   - WebSocket connections
   - gRPC for high-performance

7. **Performance improvements**
   - Further Polars optimizations
   - GPU acceleration
   - Distributed processing
   - Incremental processing

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Data Formats Guide](/openwiki/architecture/data-formats.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Development Setup](/openwiki/operations/setup.md)
- [Development Practices](/openwiki/operations/development.md)
- [Integration Guides](/openwiki/integrations/index.md)
- [Polars Integration Guide](/openwiki/integrations/polars.md)
- [Testing Overview](/openwiki/testing/overview.md)

## Quick Reference

| Component | Location | Purpose |
|-----------|----------|---------|
| CLI | `/src/fvc/tools/cli.py` | Main CLI interface with Click |
| Data File Tools | `/src/fvc/tools/df/` | Conversion, validation, correlation, fusion |
| Geospatial Calculations | `/src/fvc/tools/calc/` | Geoid, terrain, coordinate calculations |
| Visualization | `/src/fvc/tools/render/` | Map generation, interactive visualizations |
| Flight Log Analysis | `/src/fvc/tools/flightlog/` | Flight segmentation, statistics, analysis |
| Format Converters | `/src/fvc/tools/df/xformats/` | 30+ external format converters |
| Schema Validation | `/src/fvc/tools/df/schema.py` | Validate .fvc files against schemas |
| Metadata Handling | `/src/fvc/tools/df/metadata.py` | METADATA record management |
| Core Engine | `/src/fvc/tools/df/core.py` | Conversion and validation engine |
| Shared Utilities | `/src/fvc/tools/utils.py` | Shared utilities and helpers |

## Best Practices Summary

✅ **Follow modular design** - Separate concerns clearly with loose coupling
✅ **Use type hints** - Improve code clarity and IDE support
✅ **Write comprehensive tests** - Ensure reliability (aim for 80%+ coverage)
✅ **Optimize performance** - Use Polars, lazy evaluation, parallel processing
✅ **Validate rigorously** - Ensure data quality with strict schema validation
✅ **Handle errors gracefully** - Provide good error messages and continue processing
✅ **Document thoroughly** - Keep docs up to date with architecture changes
✅ **Follow security best practices** - Validate inputs, manage credentials, prevent path traversal
✅ **Monitor and log** - Track operations and performance with structured logging
✅ **Plan for evolution** - Design for extensibility and future enhancements
✅ **Use streaming I/O** - Process large files efficiently without loading into memory
✅ **Leverage Polars** - Use lazy evaluation and columnar processing for performance
✅ **Pre-compile validators** - Improve validation performance for large files

## Next Steps

- **Learn about data formats**: [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md)
- **Explore CLI tools**: [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md)
- **Set up development environment**: [/openwiki/operations/setup.md](/openwiki/operations/setup.md)
- **Run tests**: [/openwiki/testing/overview.md](/openwiki/testing/overview.md)
- **Explore integrations**: [/openwiki/integrations/index.md](/openwiki/integrations/index.md)
- **Learn about Polars integration**: [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md)
