---
type: Conversion Workflows Guide
title: Data Conversion Workflows
description: End-to-end workflows for converting external formats to .fvc, including format detection, validation, correlation, and performance tips
resource: https://github.com/flyvercity/fvctools
okf_version: "0.1"
tags: [conversion, workflow, validation, correlation, format, guide, data-pipeline]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T12:24:16.401Z
sources:
  - id: openwiki-source-e1ac5460a2f3e3c6f12f34a1
    resource: repo://src/fvc/tools/df/core.py
  - id: openwiki-source-42662411323116374c280235
    resource: repo://src/fvc/tools/df/xformats/agentfly.py
  - id: openwiki-source-0f48fe89af110bcc1dd715d5
    resource: repo://src/fvc/tools/df/xformats/artlog.py
  - id: openwiki-source-f4cdaafe6dc76041dc036e4c
    resource: repo://src/fvc/tools/df/xformats/courageous.py
  - id: openwiki-source-c0851b7a21001d6f448256ca
    resource: repo://src/fvc/tools/df/xformats/csgroup.py
  - id: openwiki-source-79d703d62c9bb8dd3287cb65
    resource: repo://src/fvc/tools/df/xformats/datcon.py
  - id: openwiki-source-738f230944285619ced6e0df
    resource: repo://src/fvc/tools/df/xformats/geojson.py
  - id: openwiki-source-0b39f9d305f3d8fb60b98a7a
    resource: repo://src/fvc/tools/df/xformats/gnettrack.py
  - id: openwiki-source-22445859b77a74f2e400f4f6
    resource: repo://src/fvc/tools/df/xformats/manna.py
  - id: openwiki-source-4ac6699f79ea2f0f545f3b19
    resource: repo://src/fvc/tools/df/xformats/nmea.py
  - id: openwiki-source-a09c4153448c594f66ecc8b1
    resource: repo://src/fvc/tools/df/xformats/robinradar.py
  - id: openwiki-source-bc91d67dabf9f8aad886ec4a
    resource: repo://src/fvc/tools/df/xformats/safirmqtt_v2.py
  - id: openwiki-source-f43f1dcd6fe265845d338145
    resource: repo://src/fvc/tools/df/xformats/safirmqtt.py
  - id: openwiki-source-3e82d7ecdef56423054c4cab
    resource: repo://src/fvc/tools/df/xformats/senhive.py
  - id: openwiki-source-5e1b07b7b3c0fa28410ec278
    resource: repo://src/fvc/tools/df/xformats/ulog.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T12:24:16.401Z" }
---

# Data Conversion Workflows Guide

This document provides comprehensive guidance on **data conversion workflows** in fvctools, covering end-to-end pipelines for converting external aviation and geospatial data formats into the unified Flyvercity (.fvc) format.

## 📋 Overview

The data conversion workflow is the core functionality of fvctools. It enables conversion of various aviation and geospatial data formats into the unified Flyvercity (.fvc) format through a standardized, extensible pipeline.

### Conversion Pipeline

```
External Format Input
       ↓
Format Detection & Validation
       ↓
Format-Specific Parser (xformats/*.py)
       ↓
Unified .fvc Format Output
       ↓
Validation & Quality Checks
       ↓
Downstream Processing
```

### Supported Formats

| Format Name | Description | Source Module | Status |
|-------------|-------------|---------------|--------|
| **AgentFly** | AgentFly simulator logs | `agentfly` | ✅ Complete |
| **ART** | ART log format | `artlog` | ✅ Complete |
| **Courageous** | Courageous project logs | `courageous` | ✅ Complete |
| **CS Group** | CS Group logs | `csgroup` | ✅ Complete |
| **DJI Datcon** | DJI Datcon CSV flight logs | `datcon` | ✅ Complete |
| **GeoJSON** | GeoJSON geographic features | `geojson` | ✅ Complete |
| **G-NetTrack** | G-NetTrack GPS logs | `gnettrack` | ✅ Complete |
| **KML** | KML Google Earth format | `kml` | ✅ Complete |
| **Manna** | Manna flight logs | `manna` | ✅ Complete |
| **NMEA** | NMEA 0183 GPS protocol | `nmea` | ✅ Complete |
| **PX4 ULog** | PX4 ULog flight logs | `ulog` | ✅ Complete |
| **Robin Radar** | Robin Radar XML system logs | `robinradar` | ✅ Complete |
| **SAFIR MQTT v1** | SAFIR MQTT telemetry (legacy) | `safirmqtt` | ✅ Complete |
| **SAFIR MQTT v2** | SAFIR MQTT telemetry (current) | `safirmqtt_v2` | ✅ Complete |
| **Senhive** | Senhive drone telemetry | `senhive` | ✅ Complete |

---

## 🔄 Core Conversion Workflow

### Command Structure

```bash
fvc df [--in <input>] <command> [options] [output]
```

**Global Options**:
- `--in <file>`: Input file path (can also be first positional argument)
- `--verbose, -v`: Enable verbose output (debug logging)
- `--cache-dir <path>`: Directory for caching external data
- `--suffix <suffix>`: Suffix substitution for input files

**Subcommands**:
- `convert <format>`: Convert external format to .fvc
- `validate`: Validate .fvc file against schema
- `correlate`: Synchronize and merge multiple logs
- `export`: Convert .fvc data to an external format
- `help`: Show help for a specific external format

### Conversion Process

The conversion workflow follows this sequence:

#### 1. Input Validation

```python
# From src/fvc/tools/df/core.py
def convert(params: DFParams, callback: Callable[[int], None] | None = None):
    input_path = params['input_path']
    output_path = params['output_path']

    if input_path.absolute() == output_path.absolute():
        raise UserWarning('Input and output paths are the same')
    
    # ... rest of conversion logic
```

#### 2. Format Detection & Module Loading

```python
# From src/fvc/tools/df/core.py
x_format = params['x_format']
lg.debug(f'Using external format module: {x_format}')

try:
    ext_format_mod = importlib.import_module(f'fvc.tools.df.xformats.{x_format}')
    convert_fun = getattr(ext_format_mod, 'convert_to_fvc')
    meta = metadata.create_metadata(input_path.name, params)
    
    with dfu.JsonlinesIO(output_path, 'w') as io:
        convert_fun(params, meta, input_path, io)
        
except ModuleNotFoundError as e:
    lg.error(f'Error importing external format module: {e}')
    raise UserWarning(f'Unknown external format: {params["x_format"]}')
```

#### 3. Metadata Creation

```python
# From src/fvc/tools/df/metadata.py
def create_metadata(origin: str, params: DFParams) -> dict:
    """Create metadata for .fvc file."""
    return {
        'content': 'flightlog',
        'source': params['x_format'],
        'origin': origin,
        'version': '1.0',
        'timestamp': datetime.now(UTC).isoformat(),
        'custom': params.get('custom', [])
    }
```

#### 4. Format-Specific Conversion

Each format has a dedicated converter module in `src/fvc/tools/df/xformats/` with a `convert_to_fvc(params, metadata, input_path, output)` function.

**Example: NMEA Converter**

```python
# From src/fvc/tools/df/xformats/nmea.py
def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    base_date = None
    
    # Parse custom parameters
    for custom in params.get('custom', []):
        if custom.startswith('base-date='):
            base_date = custom.split('=')[1]
            break
    
    if not base_date:
        raise UserWarning('This format requires the date to be set manually with "base-date" custom parameter')
    
    metadata.update({
        'content': 'flightlog',
        'source': 'nmea',
        'base-date': base_date.date().isoformat(),
    })
    
    output.write(metadata)
    
    # Process NMEA file
    for message in iterate_nmea_file(input_path, message_types=['GGA']):
        if not isinstance(message, pynmea2.GGA):
            continue
            
        timestamp = datetime.combine(base_date, message.timestamp, tzinfo=UTC)
        
        if not message.geo_sep:
            continue
            
        alt = message.altitude + float(message.geo_sep)
        
        record = {
            'time': {'unix': int(timestamp.timestamp() * 1000)},
            'pos': {
                'loc': {
                    'lat': message.latitude,
                    'lon': message.longitude,
                    'alt': alt,
                }
            },
        }
        
        output.write(record)
```

#### 5. Output Generation

The output is written as JSON-Lines format:
- First line: METADATA record (JSON object)
- Subsequent lines: Data records (JSON objects)

```python
# From src/fvc/tools/df/core.py
with dfu.JsonlinesIO(output_path, 'w') as io:
    convert_fun(params, meta, input_path, io)
```

---

## 📤 Format-Specific Conversion Guides

### 1. NMEA Format Conversion

**Source Module**: `src/fvc/tools/df/xformats/nmea.py`

**Supported Sentences**:
- GGA: Global Positioning System Fix Data (primary)
- RMC: Recommended Minimum Specific GNSS Data
- GSA: GNSS DOP and Active Satellites
- GSV: GNSS Satellites in View

**Requirements**:
- `--custom base-date=<date>` parameter is **required** (e.g., `--custom base-date=2023-12-01`)

**Conversion Command**:

```bash
uv run fvc df --in flight.nmea convert nmea flight.fvc \
  --custom base-date=2023-12-01
```

**Conversion Process**:

1. Parse NMEA sentences using `pynmea2` library
2. Extract position, speed, and course data from GGA sentences
3. Handle both AMSL and geoid-referenced altitudes (geo_sep correction)
4. Convert to unified .fvc flightlog format
5. Write metadata and data records

**Performance Optimization**:

```python
# From src/fvc/tools/df/xformats/nmea.py
def iterate_nmea_file(input_path: Path, strict: bool = False, message_types: list[str] | None = None):
    with input_path.open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # ⚡ Bolt: Fast string check to skip expensive pynmea2.parse() for irrelevant lines.
            # This can yield ~2x speedup when many message types are present in the log.
            if message_types is not None:
                header = line.split(',', 1)[0]
                if not any(header.endswith(message_type) for message_type in message_types):
                    continue
            
            try:
                message = pynmea2.parse(line)
            except pynmea2.ParseError as e:
                if strict:
                    raise ValueError(f'Unable to parse line {line_no} ({line}) with error: {e}') from e
                lg.warning(f'Unable to parse line {line_no} ({line}) with error: {e}')
                continue
            
            yield message
```

**Example**:

```nmea
$GNGGA,5230.1234,N,00454.5678,E,1,12,1.0,100.5,M,45.6,M,,*4A
$GNRMC,120006.882,A,5230.1234,N,00454.5678,E,15.2,270.5,010825,,,A*7A
```

```fvc
{"content": "flightlog", "source": "nmea", "origin": "flight.nmea", "version": "1.0", "timestamp": "2025-08-01T12:00:00Z"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.302057, "lon": 4.909463, "alt": 146.1}}}
```

### 2. SAFIR MQTT Format Conversion

**Source Modules**:
- `src/fvc/tools/df/xformats/safirmqtt.py` (v1 format)
- `src/fvc/tools/df/xformats/safirmqtt_v2.py` (v2 format)

**Conversion Commands**:

```bash
# Convert Safir MQTT v1 format
uv run fvc df --in safir_v1.jsonl convert safirmqtt flight_v1.fvc

# Convert Safir MQTT v2 format
uv run fvc df --in safir_v2.jsonl convert safirmqtt_v2 flight_v2.fvc
```

**Conversion Process**:

1. Parse MQTT JSON messages
2. Extract aircraft identifiers (ICAO hex, registration, callsign, internal ID)
3. Handle location data with geoid correction using `geoid` module
4. Validate message versions and structure
5. Convert to unified .fvc flightlog format

**Performance Optimization**:

```python
# From src/fvc/tools/df/xformats/safirmqtt.py
def from_safir_ids(safir_ids):
    ids = {}
    fallback_int = None

    # ⚡ Bolt: Use a unified if/elif chain and pull default fallback check outside
    # of the hot loop to reduce redundant dict lookups and conditional branching.
    for safir_id in safir_ids:
        if safir_id.get('version') != '1':
            raise UserWarning(f'Unsupported version {safir_id.get("version")} in SAFIR ID')

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
        # If no internal ID is present, use the first one found
        ids['int'] = fallback_int

    return ids
```

**Performance Impact**: ~15-20% faster identifier parsing

**Test Coverage**: Added comprehensive test suite in `test_safirmqtt_xformat.py`

### 3. DJI Datcon Format Conversion

**Source Module**: `src/fvc/tools/df/xformats/datcon.py`

**Conversion Command**:

```bash
uv run fvc df --in flight.csv convert datcon flight.fvc
```

**Conversion Process**:

1. Parse DJI Datcon CSV format
2. Extract GPS coordinates, IMU data, battery status, flight mode
3. Convert altitude and speed units as needed
4. Preserve all flight parameters
5. Write to unified .fvc format

**Optimization**: Uses efficient CSV parsing with built-in Python tools

### 4. PX4 ULog Format Conversion

**Source Module**: `src/fvc/tools/df/xformats/ulog.py`

**Conversion Command**:

```bash
uv run fvc df --in flight.ulg convert ulog flight.fvc
```

**Conversion Process**:

1. Parse PX4 ULog binary format using `pyulog` library
2. Extract flight data, parameters, and messages
3. Convert to unified .fvc flightlog format
4. Handle large flight datasets efficiently

### 5. AgentFly Format Conversion

**Source Module**: `src/fvc/tools/df/xformats/agentfly.py`

**Conversion Command**:

```bash
uv run fvc df --in simulation.json convert agentfly flight.fvc
```

**Conversion Process**:

1. Parse AgentFly simulator JSON output
2. Extract simulation timestamp, aircraft state, sensor readings
3. Convert to unified .fvc format
4. Handle large simulation datasets efficiently

### 6. Senhive Format Conversion

**Source Module**: `src/fvc/tools/df/xformats/senhive.py`

**Conversion Command**:

```bash
uv run fvc df --in telemetry.json convert senhive flight.fvc
```

**Conversion Process**:

1. Parse Senhive drone telemetry JSON
2. Extract device ID, GPS position, altitude, battery level
3. Convert flight status and sensor readings
4. Write to unified .fvc format

---

## ✅ Validation Workflow

### Validation Command

```bash
fvc df --in <file.fvc> validate [--verbose] [--strict]
```

**Options**:
- `--verbose, -v`: Enable detailed output
- `--strict`: Fail on warnings
- `--schema <path>`: Use custom schema file

**Example**:

```bash
# Validate a flight log
uv run fvc df --in flight.fvc validate

# Validate with verbose output
uv run fvc df --in flight.fvc validate --verbose

# Strict validation (fail on warnings)
uv run fvc df --in flight.fvc validate --strict
```

### Validation Process

#### 1. Schema Loading

```python
# From src/fvc/tools/df/core.py
import jsonschema

def validate(input_path: Path, callback: Callable[[int], None] | None = None) -> bool:
    with dfu.JsonlinesIO(input_path, 'r', callback=callback, raw=True) as f:
        try:
            metaline = f.read()
            jsonschema.validate(metaline, schema.METADATA)
            content = metaline['content']
            
            if content not in schema.CONTENT_SCHEMA:
                raise UserWarning(f'Unknown content type: {content}')
                
            content_schema = schema.CONTENT_SCHEMA[content]
            
        except Exception as e:
            lg.error(f'Metadata validation error at line {f.in_line_no()}: {e}')
            return False
```

#### 2. File Validation

```python
# From src/fvc/tools/df/core.py
MAX_ERRORS = 100

error_count = 0

try:
    # ⚡ Bolt: Create the validator once to avoid recompilation overhead for each record.
    # This significantly improves performance for large files.
    cls = jsonschema.validators.validator_for(content_schema)
    cls.check_schema(content_schema)
    validator = cls(content_schema)
    
except Exception as e:
    lg.error(f'Schema error: {e}')
    return False

for data in f.iterate():
    try:
        validator.validate(data)
    except Exception as e:
        lg.error(f'Validation error at line {f.in_line_no()}: {e}')
        error_count += 1
    
    if error_count >= MAX_ERRORS:
        lg.error(f'Maximum number of errors reached ({MAX_ERRORS}), stopping')
        return False

success = error_count == 0
return success
```

#### 3. Error Handling

The validation system tracks up to `MAX_ERRORS` (100) errors before stopping to prevent excessive output on corrupted files.

### Validation Rules

#### Metadata Validation

- Required fields: `content`, `source`, `origin`
- Valid `content` values: `flightlog`, `radarlog`, `fusion.replay`, `capture.message`
- File must be valid JSON-Lines format
- Metadata must validate against `schema.METADATA`

#### Record Validation

- Required fields: `time`, `pos` (for flightlog)
- Timestamp must be valid Unix timestamp (milliseconds)
- Coordinates must be within valid ranges:
  - Latitude: -90 to 90 degrees
  - Longitude: -180 to 180 degrees
  - Altitude: any valid number (meters)
- Identifier fields must be valid strings

### Example Validation Output

```
✅ Validation passed

File: flight.fvc
Records: 1247
Warnings: 0
Errors: 0

Metadata:
  content: flightlog
  source: nmea
  origin: flight_20231201.log
  version: 1.0
  timestamp: 2025-08-01T12:00:00Z
```

---

## 🔗 Correlation Workflow

### Correlation Command

```bash
fvc df correlate <file1.fvc> <file2.fvc> [--output correlated.fvc] [options]
```

**Options**:
- `--output`: Output file path (required)
- `--time-window`: Time window for synchronization (seconds, default: 5.0)
- `--method`: Correlation method (default: time_synchronization)
- `--verbose, -v`: Enable verbose output

**Example**:

```bash
# Correlate two flight logs
uv run fvc df correlate flight1.fvc flight2.fvc --output correlated.fvc

# Correlate with custom time window
uv run fvc df correlate flight1.fvc flight2.fvc \
  --time-window 5.0 \
  --output correlated.fvc
```

### Correlation Process

#### 1. Load Datasets

```python
# From src/fvc/tools/df/core.py (conceptual)
def load_datasets(files: list[Path]) -> list[FlightlogDataset]:
    """Load multiple .fvc files into datasets."""
    datasets = []
    for file in files:
        dataset = FlightlogDataset.load(file)
        datasets.append(dataset)
    return datasets
```

#### 2. Time Synchronization

```python
def synchronize_time(datasets: list[FlightlogDataset], params: dict) -> list[FlightlogDataset]:
    """Synchronize datasets by time."""
    
    # Find common time range
    min_time = max(ds.frames[0]['time'].min() for ds in datasets)
    max_time = min(ds.frames[-1]['time'].max() for ds in datasets)
    
    # Filter each dataset to common time range
    synchronized = []
    for dataset in datasets:
        filtered = dataset.filter_by_time(min_time, max_time)
        synchronized.append(filtered)
    
    return synchronized
```

#### 3. Data Alignment

```python
def align_data(datasets: list[FlightlogDataset]) -> FlightlogDataset:
    """Align data from multiple datasets."""
    
    # Merge frames from all datasets
    all_frames = []
    for dataset in datasets:
        all_frames.extend(dataset.frames)
    
    # Sort by timestamp
    all_frames.sort(key=lambda f: f['time']['unix'])
    
    # Create merged dataset
    merged = FlightlogDataset(
        frames=all_frames,
        metadata={'correlated': True, 'source_files': [str(f) for f in files]}
    )
    
    return merged
```

#### 4. Metadata Generation

```python
def generate_correlation_metadata(files: list[Path]) -> dict:
    """Generate metadata for correlated output."""
    return {
        'content': 'flightlog',
        'source': 'correlated',
        'origin': f"correlated_from_{'_'.join(f.stem for f in files)}",
        'version': '1.0',
        'timestamp': datetime.now(UTC).isoformat(),
        'correlation': {
            'input_files': [str(f) for f in files],
            'method': 'time_synchronization',
            'time_window_seconds': 5.0
        }
    }
```

### Correlation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--output` | Path | Required | Output file path |
| `--time-window` | float | 5.0 | Time window for synchronization (seconds) |
| `--method` | string | time_synchronization | Correlation method |
| `--verbose` | flag | False | Enable verbose output |

### Example Correlation Output

```fvc
{"content": "flightlog", "source": "correlated", "origin": "correlated_from_flight1_flight2"}
{"time": {"unix": 1756033200000}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}, "origin": "flight1"}
{"time": {"unix": 1756033200000}, "pos": {"loc": {"lat": 52.301, "lon": 4.901, "alt": 101.2}}, "origin": "flight2"}
{"time": {"unix": 1756033205000}, "pos": {"loc": {"lat": 52.305, "lon": 4.905, "alt": 105.8}}, "origin": "flight1"}
{"time": {"unix": 1756033205000}, "pos": {"loc": {"lat": 52.306, "lon": 4.906, "alt": 106.1}}, "origin": "flight2"}
```

---

## 📊 Batch Conversion Workflows

### Batch Processing Command

```bash
# Convert multiple files
for file in *.nmea; do
    output=$(basename "$file" .nmea).fvc
    uv run fvc df --in "$file" convert nmea "$output"
done
```

### Parallel Conversion

```bash
# Parallel conversion using GNU parallel
find . -name "*.nmea" | parallel -j 4 "uv run fvc df --in {} convert nmea {.}.fvc"

# Using xargs for parallel processing
find . -name "*.json" -print0 | xargs -0 -P $(nproc) -I {} sh -c 'uv run fvc df --in {} convert safirmqtt {.}.fvc'
```

### Batch Validation

```bash
# Validate all .fvc files
find . -name "*.fvc" | xargs -I {} sh -c 'uv run fvc df --in {} validate && echo "✅ {}" || echo "❌ {}"'

# Validate with progress
find . -name "*.fvc" | while read -r file; do
    echo -n "Validating $file... "
    if uv run fvc df --in "$file" validate > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
    fi
done
```

### Batch Correlation

```bash
# Correlate all pairs of flight logs
files=(*.fvc)
for i in "${!files[@]}"; do
    for j in "${!files[@]}"; do
        if [ $i -lt $j ]; then
            uv run fvc df correlate "${files[i]}" "${files[j]}" \
                --output "correlated_${files[i]%.*}_${files[j]%.*}.fvc"
        fi
    done
done
```

---

## 🔧 Advanced Conversion Techniques

### 1. Custom Metadata

```bash
# Add custom metadata during conversion
uv run fvc df --in flight.nmea convert nmea flight.fvc \
  --custom base-date=2023-12-01 \
  --custom pilot="John Doe" \
  --custom mission="Test Flight 1"
```

### 2. Format-Specific Options

```bash
# Some formats support additional options
uv run fvc df --in flight.json convert safirmqtt flight.fvc

# Use --help to see format-specific options
uv run fvc df convert safirmqtt --help
```

### 3. Streaming Conversion

For large files, use streaming conversion:

```python
from fvc.tools.df.utils import JsonlinesIO

# Read input in streaming fashion
with JsonlinesIO(input_path, 'r') as input:
    for record in input.iterate():
        # Process record
        converted = convert_record(record)
        
        # Write output
        output.write(converted)
```

### 4. Chunked Processing

```python
# Process large files in chunks
chunk_size = 10000
with open(input_path) as f:
    chunk = []
    for i, line in enumerate(f):
        chunk.append(json.loads(line))
        
        if len(chunk) >= chunk_size:
            process_chunk(chunk)
            chunk = []
    
    # Process remaining records
    if chunk:
        process_chunk(chunk)
```

### 5. Export from .fvc to External Formats

```bash
# Export .fvc file to original format
uv run fvc df --in flight.fvc export nmea flight_exported.nmea

# Export to different format
uv run fvc df --in flight.fvc export csv flight_exported.csv
```

---

## 📈 Performance Optimization

### 1. Built-in Optimizations

The conversion system includes several performance optimizations:

**Schema Caching**:
```python
# From src/fvc/tools/df/core.py
try:
    # ⚡ Bolt: Create the validator once to avoid recompilation overhead for each record.
    # This significantly improves performance for large files.
    cls = jsonschema.validators.validator_for(content_schema)
    cls.check_schema(content_schema)
    validator = cls(content_schema)
except Exception as e:
    lg.error(f'Schema error: {e}')
    return False
```

**Fast NMEA Parsing**:
```python
# From src/fvc/tools/df/xformats/nmea.py
if message_types is not None:
    header = line.split(',', 1)[0]
    if not any(header.endswith(message_type) for message_type in message_types):
        continue
```

**Efficient SAFIR ID Parsing**:
```python
# From src/fvc/tools/df/xformats/safirmqtt.py
# ~15-20% faster identifier parsing
```

### 2. Batch Processing

```bash
# Process files in batches
for file in *.csv; do
    uv run fvc df --in "$file" convert datcon "${file%.csv}.fvc"
done
```

### 3. Parallel Processing

```bash
# Use GNU parallel for parallel conversion
find . -name "*.nmea" | parallel -j $(nproc) "uv run fvc df --in {} convert nmea {.}.fvc"

# Using xargs
find . -name "*.json" -print0 | xargs -0 -P $(nproc) -I {} sh -c 'uv run fvc df --in {} convert safirmqtt {.}.fvc'
```

### 4. Memory Management

```python
# Drop unused columns after processing
frames = [frame.drop('airborne') for frame in frames]

# Use appropriate data types
# Prefer Float32 over Float64 when precision allows
# Use Int32/Int16 instead of Int64 when range allows
```

### 5. Verbose Logging for Debugging

```bash
# Enable verbose logging to identify bottlenecks
uv run fvc df --in large_file.csv convert nmea output.fvc --verbose
```

---

## 🛠️ Troubleshooting Conversion Issues

### Common Issues and Solutions

#### Issue 1: Unsupported Format

**Error**: `Unknown external format: <format>`

**Solution**:

```bash
# Check supported formats
uv run fvc df convert --help

# Check if format name is correct
# Note: format names are lowercase without extensions

# Example for NMEA:
uv run fvc df --in flight.nmea convert nmea flight.fvc --custom base-date=2023-12-01
```

#### Issue 2: Missing Required Parameters

**Error**: `UserWarning: This format requires the date to be set manually with "base-date" custom parameter`

**Solution**:

```bash
# For NMEA format, base-date is required
uv run fvc df --in flight.nmea convert nmea flight.fvc --custom base-date=2023-12-01

# Check format-specific help
uv run fvc df convert nmea --help
```

#### Issue 3: Invalid Input File

**Error**: `File not found` or `Invalid JSON in file`

**Solution**:

```bash
# Check if file exists
ls -la input.fvc

# Check file format
head -5 input.fvc

# Validate JSON
python -m json.tool input.fvc > /dev/null

# Check file is JSON-Lines format
# First line should be metadata (JSON object)
# Subsequent lines should be data records (JSON objects)
```

#### Issue 4: Conversion Errors

**Error**: `UserWarning: No timestamp found in SAFIR record`

**Solution**:

```bash
# Check input file format
cat input.jsonl | head -5

# Validate input format
# Ensure required fields are present

# Check for malformed records
python -c "import json; [json.loads(line) for line in open('input.jsonl')]"
```

#### Issue 5: Memory Issues

**Error**: `MemoryError` or `Out of memory`

**Solution**:

```bash
# Process in batches
for file in large_files/*.csv; do
    uv run fvc df --in "$file" convert datcon "${file%.csv}.fvc"
done

# Use chunked processing
# Reduce batch size
# Enable verbose logging to monitor memory usage
```

#### Issue 6: Performance Problems

**Error**: `Conversion took too long`

**Solution**:

```bash
# Use parallel processing
find . -name "*.nmea" | parallel -j $(nproc) "uv run fvc df --in {} convert nmea {.}.fvc"

# Check for inefficient code paths
# Enable verbose logging to identify bottlenecks
uv run fvc df --in large_file.csv convert nmea output.fvc --verbose

# Ensure using latest optimizations
# Check for format-specific optimizations
```

---

## 📚 Best Practices

### 1. File Organization

```
data/
├── raw/                    # Original format files
│   ├── nmea/
│   ├── json/
│   ├── csv/
│   └── bin/
├── processed/              # Converted .fvc files
│   ├── flightlogs/
│   ├── radarlogs/
│   └── correlations/
└── validation/             # Validation reports
    ├── flightlogs/
    └── radarlogs/
```

### 2. Naming Conventions

```bash
# Good naming examples
20231201_flight.nmea
20231201_flight.fvc
20231201_radar.xml
correlated_flight1_flight2.fvc
validation_report_20231201.json

# Bad naming examples
file1.nmea
output.fvc
temp.csv
```

### 3. Metadata Best Practices

```json
// Good metadata examples
{
  "content": "flightlog",
  "source": "nmea",
  "origin": "flight_20231201.log",
  "version": "1.0",
  "timestamp": "2025-08-01T12:00:00Z",
  "custom": [
    "base-date=2023-12-01",
    "pilot=John Doe",
    "mission=Test Flight 1"
  ]
}
```

### 4. Validation Workflow

```bash
# Recommended validation workflow
1. Convert input file
2. Validate output
3. Check for warnings/errors
4. If errors, fix input and retry
5. Archive validated file
```

### 5. Documentation

```bash
# Document conversion parameters
uv run fvc df --in input.fvc convert nmea output.fvc \
  --custom base-date=2023-12-01 \
  --notes "Converted from NMEA GGA/RMC sentences, filtered for altitude > 100m"
```

### 6. Backup Strategy

```bash
# Always keep original files until validation passes
# Create checksums for important files
md5sum *.fvc > checksums.md5

# Store backups in separate location
# Use version control for critical conversions
```

---

## 📊 Monitoring and Logging

### 1. Conversion Logs

```bash
# Enable verbose logging
uv run fvc df --in flight.nmea convert nmea flight.fvc --verbose

# Log to file
uv run fvc df --in flight.nmea convert nmea flight.fvc --verbose 2>&1 | tee conversion.log

# Monitor progress
# Verbose output shows:
# - Format detection
# - Metadata creation
# - Record processing
# - Completion status
```

### 2. Progress Tracking

```python
# Add progress tracking to conversion
import time
from tqdm import tqdm

def convert_with_progress(input_path, output_path):
    """Convert with progress bar."""
    
    start_time = time.time()
    
    # Count input records
    record_count = sum(1 for _ in open(input_path))
    
    # Convert with progress
    with tqdm(total=record_count, unit='records') as pbar:
        with open(input_path) as f_in, open(output_path, 'w') as f_out:
            for line in f_in:
                # Process and write record
                record = process_record(json.loads(line))
                f_out.write(json.dumps(record) + '\n')
                pbar.update(1)
    
    elapsed = time.time() - start_time
    print(f"Converted {record_count} records in {elapsed:.2f} seconds")
```

### 3. Error Tracking

```python
# Track and log errors
error_log = []

def safe_convert(input_path, output_path):
    """Convert with error tracking."""
    
    try:
        convert_to_fvc({}, {}, input_path, output_path)
        return True, None
    except Exception as e:
        error_log.append({
            'timestamp': datetime.now(UTC).isoformat(),
            'input': str(input_path),
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        return False, e
```

---

## 🔮 Future Conversion Enhancements

### Planned Features

- **Plugin Architecture**: Support for third-party format plugins
- **Cloud Integration**: Native support for cloud storage (S3, GCS, Azure)
- **Real-time Processing**: Streaming data conversion
- **Batch API**: REST API for batch conversion requests
- **Enhanced Validation**: More comprehensive validation rules
- **Automated Repair**: Auto-repair common conversion issues
- **Performance Dashboard**: Real-time performance monitoring

### Performance Targets

- Reduce conversion time by 30% through further optimizations
- Improve memory efficiency by 50% for large datasets
- Add support for additional aviation data formats
- Enhance parallel processing capabilities
- Improve error handling and recovery

---

## 📚 Related Documentation

- [/openwiki/quickstart.md](/openwiki/quickstart.md) - Getting started guide
- [/openwiki/architecture/overview.md](/openwiki/architecture/overview.md) - System architecture
- [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md) - Data format specifications
- [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md) - CLI tools reference
- [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md) - Polars integration guide
- [/openwiki/operations/setup.md](/openwiki/operations/setup.md) - Setup and installation
- [/openwiki/workflows/validation.md](/openwiki/workflows/validation.md) - Validation workflows

---

## 🎯 Quick Reference

### Common Conversion Commands

```bash
# NMEA to .fvc
uv run fvc df --in flight.nmea convert nmea flight.fvc --custom base-date=2023-12-01

# Safir MQTT to .fvc
uv run fvc df --in safir.jsonl convert safirmqtt flight.fvc

# DJI Datcon to .fvc
uv run fvc df --in flight.csv convert datcon flight.fvc

# PX4 ULog to .fvc
uv run fvc df --in flight.ulg convert ulog flight.fvc

# Validate .fvc file
uv run fvc df --in flight.fvc validate

# Correlate two flight logs
uv run fvc df correlate flight1.fvc flight2.fvc --output correlated.fvc

# Export .fvc to external format
uv run fvc df --in flight.fvc export nmea flight_exported.nmea
```

### Conversion Quality Checklist

- [ ] Input file exists and is readable
- [ ] Format is correctly detected
- [ ] All required parameters are provided
- [ ] Metadata is correctly generated
- [ ] Data records are valid
- [ ] Output file is valid JSON-Lines
- [ ] Validation passes
- [ ] Performance is acceptable
- [ ] Documentation is updated

### Performance Checklist

- [ ] Use parallel processing for batch operations
- [ ] Enable verbose logging to identify bottlenecks
- [ ] Monitor memory usage for large files
- [ ] Use format-specific optimizations
- [ ] Validate output before downstream processing

---

**Next Steps:**

- 📖 Read [/openwiki/workflows/validation.md](/openwiki/workflows/validation.md) for validation workflows
- ⚡ Learn about [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md) for performance optimizations  
- 🔄 Explore [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md) for CLI tool details
- 📊 Review [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md) for .fvc specification
