---
type: Architecture Guide
title: Architecture Overview

description: Comprehensive overview of fvctools architecture, components, and design principles
resource: /src/fvc

tags: [architecture, design, components, patterns]
---

# Architecture Overview

This guide provides a comprehensive overview of the **fvctools** architecture, including components, design patterns, and integration points.

## Overview

fvctools is a **modular Python-based CLI suite** designed for processing, converting, and validating geospatial aviation data. It serves as the backbone of Flyvercity's data pipeline, enabling seamless data integration and analysis across different platforms and formats.

## Architecture Principles

### 1. Modular Design

fvctools follows **modular architecture** principles:

- ✅ **Separation of concerns**: Each module has a single responsibility
- ✅ **Loose coupling**: Modules interact through well-defined interfaces
- ✅ **High cohesion**: Related functionality is grouped together
- ✅ **Reusability**: Components can be reused across the codebase

### 2. CLI-Centric

The primary interface is the **command-line interface (CLI)**:

- ✅ **Click framework**: Modern CLI framework with help generation
- ✅ **Subcommands**: Organized by toolset (df, calc, render)
- ✅ **Consistent interface**: Uniform argument parsing and error handling
- ✅ **Scriptable**: Easy to integrate into larger workflows

### 3. Data-Centric

All operations revolve around the **Flyvercity Data Format (.fvc)**:

- ✅ **Unified format**: Single format for all aviation data
- ✅ **JSON-Lines**: Human-readable and machine-processable
- ✅ **Schema validation**: Strict validation against schemas
- ✅ **Metadata-first**: METADATA record describes file content

### 4. Performance-Optimized

Recent commits show a focus on **performance optimizations**:

- ✅ **Polars integration**: High-performance DataFrame operations
- ✅ **Lazy evaluation**: Memory-efficient processing
- ✅ **Parallel processing**: Multi-core utilization
- ✅ **Streaming where possible**: Process large files efficiently

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                        fvctools CLI                           │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│    fvc df       │    fvc calc     │   fvc render    │  fvc    │
│  (Data File)    │ (Calculations)  │ (Visualization) │  tools  │
└────────┬────────┴────────┬────────┴────────┬────────┴─────────┘
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  /src/fvc/tools/│ │ /src/fvc/   │ │ /src/fvc/tools/ │
│      df/        │ │   calc/     │ │    render/      │
└────────┬────────┘ └──────┬──────┘ └───────┬─────────┘
         │                 │                │
         ▼                 ▼                ▼
┌───────────────────────────────────────────────────────────────┐
│                     Core Libraries                            │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│  Conversion     │  Validation     │  Visualization  │  Calc   │
│  Engine         │  Engine         │  Engine         │  Engine │
└────────┬────────┴────────┬────────┴────────┬────────┴─────────┘
         │                 │                 │
         ▼                 ▼                 ▼
┌───────────────────────────────────────────────────────────────┐
│                     Data Format (.fvc)                         │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────┐  │
│  │  METADATA   │    │  FLIGHTLOG  │    │    RADARLOG       │  │
│  │  Record     │    │  Record     │    │    Record         │  │
│  └─────────────┘    └─────────────┘    └───────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. CLI Layer

**Location**: `/src/fvc/tools/cli.py`

**Responsibilities**:
- Parse command-line arguments
- Route to appropriate toolset
- Handle global options
- Display help and version information

**Key Components**:

```python
# /src/fvc/tools/cli.py

import click

@click.group()
def main():
    """Flyvercity CLI Tools Suite"""
    pass

@main.group()
def df():
    """Data File Tools"""
    pass

@df.command()
@click.option("--in", "input_path", help="Input file path")
@click.argument("format")
@click.argument("output_path")
def convert(input_path, format, output_path):
    """Convert external format to .fvc"""
    from fvc.tools.df.core import ConversionEngine
    engine = ConversionEngine()
    engine.convert(input_path, format, output_path)
```

### 2. Toolset Layer

Three main toolsets:

#### a) Data File Tools (`fvc df`)

**Location**: `/src/fvc/tools/df/`

**Responsibilities**:
- Convert external formats to .fvc
- Validate .fvc files
- Correlate multiple data sources
- Manage data fusion operations

**Submodules**:

```
src/fvc/tools/df/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands
├── core.py                  # Conversion engine
├── schema.py                # Schema validation
├── metadata.py              # METADATA handling
├── correlate.py             # Correlation engine
├── fusion.py                # Fusion operations
├── utils.py                 # Utility functions
└── xformats/                # Format converters
    ├── __init__.py
    ├── base.py              # Base converter class
    ├── nmea.py              # NMEA converter
    ├── ulog.py              # ULog converter
    ├── safirmqtt.py         # SAFIR MQTT converter
    ├── safirmqtt_v2.py      # Optimized SAFIR MQTT converter
    ├── datcon.py            # DatCon converter
    ├── senhive.py           # SenHive converter
    ├── agentfly.py          # AgentFly converter
    └── ...                  # Other format converters
```

**Key Classes**:

```python
# /src/fvc/tools/df/core.py

class ConversionEngine:
    """Core conversion engine"""
    
    def convert(self, input_path: str, format: str, output_path: str) -> bool:
        """Convert external format to .fvc"""
        converter = self._get_converter(format)
        return converter.convert(input_path, output_path)
    
    def _get_converter(self, format: str):
        """Get appropriate converter for format"""
        converters = {
            "nmea": NMEAConverter,
            "ulog": ULogConverter,
            "safirmqtt": SAFIRMQTTConverter,
            "safirmqtt_v2": SAFIRMQTTv2Converter,
            "datcon": DatConConverter,
            "senhive": SenHiveConverter,
            "agentfly": AgentFlyConverter,
            # ... other formats
        }
        return converters[format]()
```

#### b) Geospatial Calculations (`fvc calc`)

**Location**: `/src/fvc/tools/calc/`

**Responsibilities**:
- Geoid undulation calculations
- Terrain elevation lookups
- Coordinate transformations
- Geospatial calculations

**Submodules**:

```
src/fvc/tools/calc/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands
├── geoid.py                 # Geoid calculations
├── terrain.py               # Terrain calculations
└── utils.py                 # Utility functions
```

**Key Functions**:

```python
# /src/fvc/tools/calc/geoid.py

def get_undulation(lat: float, lon: float) -> float:
    """Get EGM96 geoid undulation at given coordinates"""
    from pygeodesy import EGM96
    geoid = EGM96()
    return geoid.height(lat, lon)

def altitude_to_amsl(altitude: float, lat: float, lon: float) -> float:
    """Convert ellipsoidal altitude to AMSL"""
    undulation = get_undulation(lat, lon)
    return altitude - undulation
```

#### c) Visualization (`fvc render`)

**Location**: `/src/fvc/tools/render/`

**Responsibilities**:
- Generate interactive maps
- Create flight path visualizations
- Export to multiple formats (HTML, KML, JSON)
- Template-based rendering

**Submodules**:

```
src/fvc/tools/render/
├── __init__.py              # Package initialization
├── cli.py                   # CLI commands
├── core.py                  # Rendering engine
├── templates.py             # Template management
└── templates/               # Jinja2 templates
    ├── flight_map.html
    ├── index.html
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
        records = self._load_fvc(input_path)
        
        # Process data
        flight_path = self._extract_flight_path(records)
        
        # Render template
        template = self._get_template("flight_map.html")
        html = template.render(
            title="Flight Map",
            flight_path=flight_path,
            waypoints=self._extract_waypoints(records)
        )
        
        # Write output
        self._write_output(html, output_dir)
    
    def _get_template(self, name: str):
        """Get Jinja2 template"""
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader("templates/"))
        return env.get_template(name)
```

### 3. Core Libraries

#### a) Format Converters

**Location**: `/src/fvc/tools/df/xformats/`

**Responsibilities**:
- Convert external formats to .fvc
- Parse format-specific data structures
- Transform to unified schema
- Handle format-specific edge cases

**Base Class**:

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
        """Write METADATA record to output file"""
        metadata = {
            "content": content,
            "source": source,
            "origin": origin,
        }
        with open(output_path, "w") as f:
            f.write(f"{metadata}\n")
    
    def _write_record(self, output_path: str, record: dict) -> None:
        """Write a single record to output file"""
        with open(output_path, "a") as f:
            f.write(f"{record}\n")
```

**Example Converter**:

```python
# /src/fvc/tools/df/xformats/nmea.py

import pynmea2
from fvc.tools.df.xformats.base import BaseConverter

class NMEAConverter(BaseConverter):
    """Convert NMEA format to .fvc"""
    
    def convert(self, input_path: str, output_path: str) -> bool:
        """Convert NMEA file to .fvc format"""
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

#### b) Schema Validation

**Location**: `/src/fvc/tools/df/schema.py`

**Responsibilities**:
- Validate .fvc files against schemas
- Check METADATA structure
- Validate data records
- Provide detailed error messages

**Key Class**:

```python
# /src/fvc/tools/df/schema.py

import json
from jsonschema import validate, ValidationError

class SchemaValidator:
    """Validate .fvc files against schemas"""
    
    def __init__(self):
        self.schema = self._load_schema()
    
    def _load_schema(self) -> dict:
        """Load schema from YAML file"""
        import yaml
        with open("src/fvc/tools/df/schema.yaml", "r") as f:
            return yaml.safe_load(f)
    
    def validate_file(self, file_path: str, verbose: bool = False) -> bool:
        """Validate .fvc file"""
        try:
            with open(file_path, "r") as f:
                # Validate METADATA
                metadata = json.loads(f.readline())
                self._validate_metadata(metadata)
                
                # Validate data records
                for line_num, line in enumerate(f, start=2):
                    record = json.loads(line)
                    self._validate_record(record, metadata["content"], line_num)
            
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

#### c) Metadata Handling

**Location**: `/src/fvc/tools/df/metadata.py`

**Responsibilities**:
- Parse METADATA records
- Validate METADATA structure
- Extract metadata fields
- Generate METADATA for output files

**Key Functions**:

```python
# /src/fvc/tools/df/metadata.py

from typing import Dict, Any
import json

class Metadata:
    """Handle METADATA records"""
    
    def __init__(self, content: str, source: str, origin: str, **extra):
        self.content = content
        self.source = source
        self.origin = origin
        self.extra = extra
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert METADATA to dict"""
        result = {
            "content": self.content,
            "source": self.source,
            "origin": self.origin,
        }
        result.update(self.extra)
        return result
    
    def to_json(self) -> str:
        """Convert METADATA to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Metadata':
        """Parse METADATA from file"""
        with open(file_path, "r") as f:
            first_line = f.readline()
            data = json.loads(first_line)
            return cls(**data)
```

### 4. Data Format (.fvc)

**The Flyvercity Data Format** is the unified format used by all tools.

**Format**: JSON-Lines (`.jsonl`)

**Structure**:

```
Line 1: METADATA record
Line 2+: Data records (FLIGHTLOG, RADARLOG, etc.)
```

**Example**:

```json
{"content": "flightlog", "source": "nmea", "origin": "flight.log"}
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

**See**: [Data Formats Guide](/openwiki/architecture/data-formats.md)

## Integration Points

### 1. External Libraries

fvctools integrates with several external libraries:

| Library | Purpose | Integration |
|---------|---------|-------------|
| **Polars** | High-performance DataFrames | Format converters (agentfly, datcon, senhive) |
| **PyGeodesy** | Geodetic calculations | Calculation tools |
| **GeoPandas** | Geospatial data manipulation | Visualization and analysis |
| **Rasterio** | DEM access | Terrain calculations |
| **PyNMEA2** | NMEA parsing | NMEA converter |
| **PyULog** | ULog parsing | ULog converter |
| **SimpleKML** | KML generation | Visualization export |
| **Jinja2** | HTML templating | Visualization rendering |
| **Click** | CLI framework | Main CLI interface |
| **JSONSchema** | Schema validation | .fvc file validation |

### 2. External Formats

fvctools supports conversion from multiple external formats:

| Format | Module | Description |
|--------|--------|-------------|
| **NMEA** | `nmea.py` | Standard GPS protocol |
| **ULog** | `ulog.py` | PX4 flight controller logs |
| **SAFIR MQTT** | `safirmqtt.py`, `safirmqtt_v2.py` | Telemetry streaming |
| **DatCon** | `datcon.py` | Flight recorder format |
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

### 3. Output Formats

fvctools can export to multiple formats:

| Format | Tool | Description |
|--------|------|-------------|
| **.fvc** | All | Unified Flyvercity Data Format |
| **HTML** | `fvc render` | Interactive maps |
| **KML** | `fvc render` | Google Earth format |
| **JSON** | `fvc render` | Data export |

### 4. CLI Integration

All toolsets integrate through the main CLI:

```bash
# Data File Tools
fvc df --in input.nmea convert nmea output.fvc
fvc df --in output.fvc validate
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc

# Geospatial Calculations
fvc calc undulation 52.3 4.9
fvc calc terrain 52.3 4.9 100.0

# Visualization
fvc render fl flight.fvc --output ./map
```

## Performance Considerations

### 1. Polars Integration

Recent commits (a456910, b3858c6, cc7819d) show heavy use of **Polars** for performance:

**Benefits**:
- ✅ **Blazing-fast operations**: Rust-based implementation
- ✅ **Lazy evaluation**: Memory-efficient processing
- ✅ **Parallel processing**: Multi-core utilization
- ✅ **Columnar storage**: Efficient memory usage

**Converters using Polars**:
- `agentfly.py` - AgentFly converter
- `datcon.py` - DatCon converter
- `senhive.py` - SenHive converter
- `safirmqtt_v2.py` - Optimized SAFIR MQTT converter

**Example**:

```python
# /src/fvc/tools/df/xformats/agentfly.py

import polars as pl

class AgentFlyConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str) -> bool:
        # Read with Polars
        df = pl.read_csv(input_path)
        
        # Transform with Polars
        df = (df
            .lazy()  # Lazy evaluation
            .with_columns(
                pl.col("timestamp").cast(pl.Int64),
                pl.col("latitude").cast(pl.Float64),
                pl.col("longitude").cast(pl.Float32),  # Use Float32 for coordinates
            )
            .filter(pl.col("timestamp").is_not_null())
            .collect()  # Materialize
        )
        
        # Write to .fvc
        self._write_fvc(df, output_path)
        return True
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

### 3. Memory Management

**Techniques**:

- ✅ **Use appropriate data types**: `Float32` instead of `Float64` for coordinates
- ✅ **Lazy evaluation**: Process data without materializing
- ✅ **Chunk processing**: Process in manageable chunks
- ✅ **Close files**: Use context managers

**Example**:

```python
# ✅ Good: Use Float32 for coordinates
pl.Float32()  # 4 bytes vs 8 bytes for Float64

# ✅ Good: Lazy evaluation
lazy_df = df.lazy()
result = lazy_df.filter(...).collect()

# ✅ Good: Chunk processing
chunk_size = 10000
for chunk in df.iter_slices(chunk_size):
    process_chunk(chunk)
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
find ./input -name "*.nmea" | parallel -j $(nproc) process_file {}

# Multiprocessing
from multiprocessing import Pool

with Pool() as pool:
    results = pool.map(process_file, file_list)
```

## Error Handling and Validation

### 1. Schema Validation

**Strict validation** ensures data quality:

```python
# /src/fvc/tools/df/schema.py

class SchemaValidator:
    def validate_file(self, file_path: str, verbose: bool = False) -> bool:
        """Validate .fvc file"""
        try:
            with open(file_path, "r") as f:
                # Validate METADATA
                metadata = json.loads(f.readline())
                self._validate_metadata(metadata)
                
                # Validate data records
                for line_num, line in enumerate(f, start=2):
                    record = json.loads(line)
                    self._validate_record(record, metadata["content"], line_num)
            
            return True
        except Exception as e:
            if verbose:
                print(f"Validation error: {e}")
            return False
```

### 2. Graceful Degradation

**Handle errors without crashing**:

```python
# /src/fvc/tools/df/xformats/nmea.py

class NMEAConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str) -> bool:
        try:
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
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return False
```

### 3. Detailed Error Messages

**Provide actionable error information**:

```python
# Good error handling
try:
    process_file(file_path)
except FileNotFoundError as e:
    logger.error(f"File not found: {file_path}")
    raise FileNotFoundError(f"Input file not found: {file_path}")
except ValidationError as e:
    logger.error(f"Validation failed at line {line_num}: {e.message}")
    raise ValueError(f"Invalid data at line {line_num}: {e.message}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
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
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

def safe_path(base_dir: str, relative_path: str) -> str:
    """Ensure path is within base directory"""
    full_path = Path(base_dir) / relative_path
    if not full_path.resolve().startswith(Path(base_dir).resolve()):
        raise ValueError("Path traversal detected")
    return str(full_path)
```

### 2. File Permissions

**Set appropriate permissions**:

```python
import os

# Set file permissions
os.chmod("output.fvc", 0o644)  # Read/write for owner, read for others

# Use umask
os.umask(0o022)  # Default: 644 for files, 755 for directories

# Run as non-root user
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

# Or use AWS credentials file
# ~/.aws/credentials
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
│   └── test_polars_integration.py
├── fixtures/                # Test data
│   ├── nmea_samples.py
│   ├── flight_records.py
│   └── schema_samples.py
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
```

### 3. Test Coverage

**Aim for 80%+ coverage**:

```bash
# Run tests with coverage
pytest --cov=src/fvc --cov-report=html

# Set minimum coverage in pytest.ini
[tool:pytest]
addopts = --cov=src/fvc --cov-report=term-missing --cov-fail-under=80
```

## Deployment Architecture

### 1. Development Deployment

**Editable install**:

```bash
# Clone repository
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Install in development mode
uv pip install -e ".[dev]"
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

**Structured logging**:

```python
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=os.getenv("FVC_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/var/log/fvctools/app.log"),
    ]
)
```

### 2. Metrics Collection

**Performance metrics**:

```python
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
df = pl.DataFrame(...)
lazy_df = df.lazy()
result = lazy_df.filter(...).collect()

# ❌ Bad: Eager evaluation (materializes intermediate results)
result = df.filter(...).collect()
result = result.group_by(...).agg(...)
```

### 2. Streaming Pattern

```python
# ✅ Good: Stream large files
with open("large_file.jsonl", "r") as f:
    for line in f:
        record = json.loads(line)
        process_record(record)

# ❌ Bad: Load entire file into memory
data = f.read()  # Large memory usage
```

### 3. Parallel Processing Pattern

```python
# ✅ Good: Use Polars parallel operations
result = df.group_by("flight_id").agg(...).collect()

# ✅ Good: Use GNU parallel for batch processing
find ./input -name "*.nmea" | parallel -j $(nproc) process_file {}

# ✅ Good: Use multiprocessing
from multiprocessing import Pool

with Pool() as pool:
    results = pool.map(process_file, file_list)
```

### 4. Caching Pattern

```python
import functools

@functools.lru_cache(maxsize=100)
def get_geoid_undulation(lat: float, lon: float) -> float:
    """Cache geoid undulation calculations"""
    from pygeodesy import EGM96
    geoid = EGM96()
    return geoid.height(lat, lon)
```

## Evolution and Future Directions

### 1. Recent Changes

Based on git history, recent changes include:

- ✅ **Polars integration** (commits a456910, b3858c6, cc7819d)
- ✅ **Performance optimizations** (commits 5db7907, ccffcac)
- ✅ **Format converter improvements** (multiple commits)
- ✅ **Schema validation enhancements**
- ✅ **Code refactoring** (commit ccffcac: "Remove redundant wrapper")

### 2. Future Enhancements

Potential future directions:

1. **Additional format converters**
   - MAVLink support
   - ArduPilot logs
   - Pixhawk logs
   - Litchi logs

2. **Cloud integration**
   - AWS S3 direct access
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

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Data Formats Guide](/openwiki/architecture/data-formats.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Development Setup](/openwiki/operations/setup.md)
- [Development Practices](/openwiki/operations/development.md)
- [Integration Guides](/openwiki/integrations/index.md)

## Quick Reference

| Component | Location | Purpose |
|-----------|----------|---------|
| CLI | `/src/fvc/tools/cli.py` | Main CLI interface |
| Data File Tools | `/src/fvc/tools/df/` | Conversion, validation, correlation |
| Geospatial Calculations | `/src/fvc/tools/calc/` | Geoid, terrain calculations |
| Visualization | `/src/fvc/tools/render/` | Map generation |
| Format Converters | `/src/fvc/tools/df/xformats/` | External format conversion |
| Schema Validation | `/src/fvc/tools/df/schema.py` | Validate .fvc files |
| Metadata Handling | `/src/fvc/tools/df/metadata.py` | METADATA record management |
| Core Engine | `/src/fvc/tools/df/core.py` | Conversion engine |

## Best Practices Summary

✅ **Follow modular design** - Separate concerns clearly
✅ **Use type hints** - Improve code clarity and IDE support
✅ **Write comprehensive tests** - Ensure reliability
✅ **Optimize performance** - Use Polars, lazy evaluation, parallel processing
✅ **Validate rigorously** - Ensure data quality
✅ **Handle errors gracefully** - Provide good error messages
✅ **Document thoroughly** - Keep docs up to date
✅ **Follow security best practices** - Validate inputs, manage credentials
✅ **Monitor and log** - Track operations and performance
✅ **Plan for evolution** - Design for extensibility

## Next Steps

- **Learn about data formats**: [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md)
- **Explore CLI tools**: [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md)
- **Set up development environment**: [/openwiki/operations/setup.md](/openwiki/operations/setup.md)
- **Run tests**: [/openwiki/testing/overview.md](/openwiki/testing/overview.md)
- **Explore integrations**: [/openwiki/integrations/index.md](/openwiki/integrations/index.md)
