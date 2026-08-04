---
type: Conversion Workflows Guide
title: Data Conversion Workflows
edescription: Comprehensive guide to data conversion workflows in fvctools, including format conversion, validation, correlation, and best practices
resource: https://github.com/flyvercity/fvctools
okf_version: "0.1"
tags: [conversion, workflow, validation, correlation, format, guide]
---

# Data Conversion Workflows Guide

This document provides comprehensive guidance on data conversion workflows in fvctools, including format conversion, validation, correlation, and best practices.

## 📋 Overview

The data conversion workflow is the core functionality of fvctools. It enables conversion of various aviation and geospatial data formats into the unified Flyvercity (.fvc) format.

### Conversion Pipeline

```
External Format Input
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
| **DJI Datcon** | DJI Datcon logs | `datcon` | ✅ Complete |
| **GeoJSON** | GeoJSON format | `geojson` | ✅ Complete |
| **Gnettrack** | Gnettrack logs | `gnettrack` | ✅ Complete |
| **NMEA** | NMEA GPS logs | `nmea` | ✅ Complete |
| **Robin Radar** | Robin Radar XML | `robinradar` | ✅ Complete |
| **Safir MQTT** | Safir MQTT logs | `safirmqtt` (v1), `safirmqtt_v2` (v2) | ✅ Complete |
| **Senhive** | Senhive logs | `senhive` | ✅ Complete |
| **PX4 ULog** | PX4 ULog logs | `ulog` | ✅ Complete |

---

## 🔄 Core Conversion Workflow

### Command Structure

```bash
fvc df [--in <input>] <command> [options] [output]
```

**Global Options**:
- `--in <file>`: Input file path
- `--verbose`: Enable verbose output
- `--quiet`: Suppress non-essential output

**Subcommands**:
- `convert <format>`: Convert external format to .fvc
- `validate`: Validate .fvc file against schema
- `correlate`: Synchronize and merge multiple logs

### Conversion Process

#### 1. Input Validation

```python
# Check if input file exists
if not input_path.exists():
    raise FileNotFoundError(f"Input file not found: {input_path}")

# Check file format
if not is_supported_format(input_path):
    raise ValueError(f"Unsupported format: {input_path.suffix}")
```

#### 2. Format Detection

```python
def detect_format(input_path: Path) -> str:
    """Detect format from file extension or content."""
    
    extension_map = {
        '.nmea': 'nmea',
        '.ulg': 'ulog',
        '.csv': 'datcon',
        '.json': 'safirmqtt',
        '.jsonl': 'safirmqtt',
        '.geojson': 'geojson',
        '.xml': 'robinradar',
    }
    
    # Check extension
    if input_path.suffix.lower() in extension_map:
        return extension_map[input_path.suffix.lower()]
    
    # Check content (fallback)
    # ... content-based detection ...
    
    raise ValueError(f"Could not detect format from {input_path}")
```

#### 3. Format-Specific Conversion

```python
# Import appropriate converter
if format == 'nmea':
    from fvc.tools.df.xformats.nmea import convert_to_fvc
elif format == 'safirmqtt':
    from fvc.tools.df.xformats.safirmqtt import convert_to_fvc as convert_to_fvc_v1
    from fvc.tools.df.xformats.safirmqtt_v2 import convert_to_fvc as convert_to_fvc_v2
    # Choose v1 or v2 based on input
    convert_to_fvc = convert_to_fvc_v2 if is_v2_format(input_path) else convert_to_fvc_v1
# ... other formats ...

# Run conversion
convert_to_fvc(params, metadata, input_path, output)
```

#### 4. Output Generation

```python
# Write metadata line (first line)
metadata = {
    'content': 'flightlog',
    'source': format,
    'origin': str(input_path),
    'version': '1.0',
    'timestamp': datetime.now().isoformat()
}
output.write(metadata)

# Write data records
for record in converted_records:
    output.write(record)
```

---

## 📤 Format-Specific Conversion Guides

### 1. NMEA Format Conversion

**Source Module**: `src/fvc/tools/df/xformats/nmea.py`

**Supported Sentences**:
- GGA: Global Positioning System Fix Data
- RMC: Recommended Minimum Specific GNSS Data
- GSA: GNSS DOP and Active Satellites
- GSV: GNSS Satellites in View

**Conversion Command**:

```bash
uv run fvc df --in flight.nmea convert nmea flight.fvc
```

**Conversion Process**:

1. Parse NMEA sentences
2. Extract position, speed, and course data
3. Handle both AMSL and geoid-referenced altitudes
4. Convert to unified .fvc flightlog format
5. Write metadata and data records

**Example**:

```nmea
$GNGGA,5230.1234,N,00454.5678,E,1,12,1.0,100.5,M,45.6,M,,*4A
$GNRMC,120006.882,A,5230.1234,N,00454.5678,E,15.2,270.5,010825,,,A*7A
```

```fvc
{"content": "flightlog", "source": "nmea", "origin": "flight.nmea"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.302057, "lon": 4.909463, "alt": 100.5}}, "origin": "flight.nmea"}
```

### 2. Safir MQTT Format Conversion

**Source Modules**:
- `src/fvc/tools/df/xformats/safirmqtt.py` (v1 format)
- `src/fvc/tools/df/xformats/safirmqtt_v2.py` (v2 format)

**Conversion Commands**:

```bash
# Convert Safir MQTT v1 format
uv run fvc df --in safir_v1.jsonl convert safirmqtt flight_v1.fvc

# Convert Safir MQTT v2 format
uv run fvc df --in safir_v2.jsonl convert safirmqtt flight_v2.fvc
```

**Conversion Process**:

1. Parse MQTT JSON messages
2. Extract aircraft identifiers (ICAO hex, registration, callsign, internal ID)
3. Handle location data with geoid correction
4. Validate message versions and structure
5. Convert to unified .fvc flightlog format

**Recent Optimizations**:

The `from_safir_ids` function was optimized for performance:

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

**Optimization**: Uses Polars for efficient CSV parsing and processing

### 4. AgentFly Format Conversion

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

**Optimization**: Uses Polars for efficient JSON processing

### 5. Senhive Format Conversion

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
fvc df --in <file.fvc> validate [--verbose]
```

**Example**:

```bash
# Validate a flight log
uv run fvc df --in flight.fvc validate

# Validate with verbose output
uv run fvc df --in flight.fvc validate --verbose
```

### Validation Process

#### 1. Schema Loading

```python
def load_schema(schema_path: Path | None = None) -> dict:
    """Load JSON Schema for validation."""
    
    if schema_path:
        with open(schema_path) as f:
            return json.load(f)
    
    # Load default schema
    return load_default_schema()
```

#### 2. File Validation

```python
def validate_fvc(input_path: Path, schema: dict) -> ValidationResult:
    """Validate .fvc file against schema."""
    
    # Check if file exists
    if not input_path.exists():
        return ValidationResult(False, "File not found")
    
    # Check file format (JSON-Lines)
    if not is_jsonlines(input_path):
        return ValidationResult(False, "Not a valid JSON-Lines file")
    
    # Validate metadata line
    metadata = read_first_line(input_path)
    if not validate_metadata(metadata, schema):
        return ValidationResult(False, "Invalid metadata")
    
    # Validate data records
    for line_num, line in enumerate_file(input_path):
        if line_num == 0:
            continue  # Skip metadata
        
        record = json.loads(line)
        if not validate_record(record, schema):
            return ValidationResult(False, f"Invalid record at line {line_num}")
    
    return ValidationResult(True, "Validation passed")
```

#### 3. Error Reporting

```python
class ValidationResult:
    def __init__(self, valid: bool, message: str, errors: list | None = None):
        self.valid = valid
        self.message = message
        self.errors = errors or []
    
    def add_error(self, error: ValidationError):
        self.errors.append(error)
    
    def format_errors(self) -> str:
        """Format validation errors for display."""
        if not self.errors:
            return ""
        
        error_messages = []
        for error in self.errors:
            error_messages.append(
                f"Line {error.line}: {error.message} (field: {error.field}, value: {error.value})"
            )
        
        return "\n".join(error_messages)
```

### Validation Rules

#### Metadata Validation

- Required fields: `content`, `source`, `origin`
- Valid `content` values: `flightlog`, `radarlog`, `metadata`, `eventlog`
- File must be valid JSON-Lines format

#### Record Validation

- Required fields: `time`, `pos` (for flightlog)
- Timestamp must be valid Unix timestamp
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

**Example**:

```bash
# Correlate two flight logs
uv run fvc df correlate flight1.fvc flight2.fvc --output correlated.fvc

# Correlate with custom parameters
uv run fvc df correlate flight1.fvc flight2.fvc \
  --time-window 5.0 \
  --output correlated.fvc
```

### Correlation Process

#### 1. Load Datasets

```python
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
        'timestamp': datetime.now().isoformat(),
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
```

### Batch Validation

```bash
# Validate all .fvc files
find . -name "*.fvc" | xargs -I {} sh -c 'uv run fvc df --in {} validate && echo "✅ {}" || echo "❌ {}"'
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
  --metadata '{"pilot": "John Doe", "mission": "Test Flight 1"}'
```

### 2. Format-Specific Options

```bash
# Some formats support additional options
uv run fvc df --in flight.json convert safirmqtt flight.fvc \
  --safir-version 2
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

---

## 📈 Performance Optimization

### 1. Use Polars for Efficient Processing

```python
# Good: Use Polars DataFrames
import polars as pl

df = pl.read_csv("large_file.csv")
result = df.filter(...).group_by(...).agg(...)

# Bad: Use pandas (slower and less memory efficient)
import pandas as pd

df = pd.read_csv("large_file.csv")
result = df[df['altitude'] > 100].groupby('icaohex').mean()
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
```

### 4. Memory Management

```python
# Drop unused columns after processing
frames = [frame.drop('airborne') for frame in frames]

# Use appropriate data types
schema = {
    "altitude": pl.Float32,  # Use Float32 instead of Float64
    "latitude": pl.Float64,
    "longitude": pl.Float64
}
```

---

## 🛠️ Troubleshooting Conversion Issues

### Common Issues and Solutions

#### Issue 1: Unsupported Format

**Error**: `Unsupported format: .unknown`

**Solution**:

```bash
# Check supported formats
uv run fvc df convert --help

# Use correct format name
uv run fvc df --in file.unknown convert nmea output.fvc
```

#### Issue 2: Invalid Input File

**Error**: `File not found: input.fvc` or `Invalid JSON in file`

**Solution**:

```bash
# Check if file exists
ls -la input.fvc

# Check file format
head -5 input.fvc

# Validate JSON
python -m json.tool input.fvc > /dev/null
```

#### Issue 3: Conversion Errors

**Error**: `UserWarning: No timestamp found in SAFIR record`

**Solution**:

```bash
# Check input file format
cat input.jsonl | head -5

# Validate input format
# Ensure required fields are present
```

#### Issue 4: Memory Issues

**Error**: `MemoryError` or `Out of memory`

**Solution**:

```bash
# Process in batches
for file in large_files/*.csv; do
    uv run fvc df --in "$file" convert datcon "${file%.csv}.fvc"
done

# Use chunked processing
# Reduce batch size
```

#### Issue 5: Performance Problems

**Error**: `Conversion took too long`

**Solution**:

```bash
# Use Polars-based converters
# Process in parallel
# Use batch processing
# Check for inefficient code paths
```

---

## 📚 Best Practices

### 1. File Organization

```
data/
├── raw/                    # Original format files
│   ├── nmea/
│   ├── json/
│   └── csv/
├── processed/              # Converted .fvc files
│   ├── flightlogs/
│   ├── radarlogs/
│   └── correlations/
└── validation/             # Validation reports
    ├── flightlogs/
    └── radarlogs/
```

### 2. Naming Conventions

```
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
  "metadata": {
    "pilot": "John Doe",
    "aircraft": "N12345",
    "mission": "Test Flight 1"
  }
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
  --notes "Converted from NMEA GGA/RMC sentences, filtered for altitude > 100m"
```

---

## 🔄 Conversion Quality Assurance

### Quality Metrics

Track these metrics for conversion quality:

#### 1. Conversion Success Rate

```bash
# Track success rate
total_files=100
successful_conversions=98
success_rate=$((successful_conversions * 100 / total_files))

echo "Conversion success rate: $success_rate%"
```

#### 2. Data Loss

```python
# Calculate data loss
def calculate_data_loss(original_count: int, converted_count: int) -> float:
    """Calculate percentage of data loss."""
    if original_count == 0:
        return 0.0
    return ((original_count - converted_count) / original_count) * 100
```

#### 3. Accuracy

```python
# Calculate accuracy (if ground truth available)
def calculate_accuracy(converted_data, ground_truth) -> float:
    """Calculate accuracy compared to ground truth."""
    # Implement accuracy calculation based on data type
    # For position data: calculate distance between points
    # For altitude: calculate difference
    return accuracy_score
```

#### 4. Performance Metrics

```bash
# Measure conversion time
/usr/bin/time -v uv run fvc df --in large_file.csv convert nmea output.fvc

# Track memory usage
# Use memory profiler
```

### Quality Checks

#### 1. Schema Validation

```bash
# Validate against schema
uv run fvc df --in output.fvc validate
```

#### 2. Data Consistency

```python
# Check data consistency
def check_consistency(dataset: FlightlogDataset) -> bool:
    """Check if dataset is consistent."""
    
    # Check timestamps are in order
    timestamps = [f['time']['unix'] for f in dataset.frames]
    if timestamps != sorted(timestamps):
        return False
    
    # Check coordinates are within valid ranges
    for frame in dataset.frames:
        lat = frame['pos']['loc']['lat']
        lon = frame['pos']['loc']['lon']
        
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
    
    return True
```

#### 3. Completeness

```python
# Check data completeness
def check_completeness(dataset: FlightlogDataset, expected_count: int) -> bool:
    """Check if all expected records are present."""
    return len(dataset.frames) == expected_count
```

---

## 🚀 Automation and Scripting

### 1. Conversion Script

```bash
#!/bin/bash
# convert_all.sh - Convert all supported formats in a directory

INPUT_DIR="$1"
OUTPUT_DIR="$2"

mkdir -p "$OUTPUT_DIR"

# Convert NMEA files
for file in "$INPUT_DIR"/*.nmea; do
    if [ -f "$file" ]; then
        output="$OUTPUT_DIR/$(basename "$file" .nmea).fvc"
        echo "Converting NMEA: $file -> $output"
        uv run fvc df --in "$file" convert nmea "$output"
    fi
done

# Convert JSON files (Safir MQTT)
for file in "$INPUT_DIR"/*.json; do
    if [ -f "$file" ]; then
        output="$OUTPUT_DIR/$(basename "$file" .json).fvc"
        echo "Converting JSON: $file -> $output"
        uv run fvc df --in "$file" convert safirmqtt "$output"
    fi
done

# Convert CSV files (DJI Datcon)
for file in "$INPUT_DIR"/*.csv; do
    if [ -f "$file" ]; then
        output="$OUTPUT_DIR/$(basename "$file" .csv).fvc"
        echo "Converting CSV: $file -> $output"
        uv run fvc df --in "$file" convert datcon "$output"
    fi
done

echo "Conversion complete!"
```

### 2. Validation Script

```bash
#!/bin/bash
# validate_all.sh - Validate all .fvc files in a directory

INPUT_DIR="$1"

success_count=0
fail_count=0

for file in "$INPUT_DIR"/*.fvc; do
    if [ -f "$file" ]; then
        echo -n "Validating $file... "
        if uv run fvc df --in "$file" validate; then
            echo "✅"
            ((success_count++))
        else
            echo "❌"
            ((fail_count++))
        fi
    fi
done

echo "Validation complete: $success_count successful, $fail_count failed"
```

### 3. Batch Processing Script

```python
#!/usr/bin/env python3
# batch_convert.py - Batch convert files with progress tracking

import os
import json
from pathlib import Path
from fvc.tools.df.xformats.nmea import convert_to_fvc

def batch_convert(input_dir: str, output_dir: str):
    """Batch convert all NMEA files in directory."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    converted = 0
    failed = 0
    
    for nmea_file in input_path.glob('*.nmea'):
        try:
            output_file = output_path / f"{nmea_file.stem}.fvc"
            
            print(f"Converting {nmea_file.name}...")
            
            with open(output_file, 'w') as out_f:
                from fvc.tools.df.utils import JsonlinesIO
                
                metadata = {
                    'content': 'flightlog',
                    'source': 'nmea',
                    'origin': str(nmea_file),
                    'version': '1.0'
                }
                
                with JsonlinesIO(output_file, 'w') as output:
                    convert_to_fvc({}, metadata, nmea_file, output)
            
            converted += 1
            print(f"✅ {nmea_file.name} -> {output_file.name}")
            
        except Exception as e:
            failed += 1
            print(f"❌ {nmea_file.name}: {e}")
    
    print(f"\nConversion complete: {converted} converted, {failed} failed")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python batch_convert.py <input_dir> <output_dir>")
        sys.exit(1)
    
    batch_convert(sys.argv[1], sys.argv[2])
```

---

## 📊 Monitoring and Logging

### 1. Conversion Logs

```bash
# Enable verbose logging
uv run fvc df --in flight.nmea convert nmea flight.fvc --verbose

# Log to file
uv run fvc df --in flight.nmea convert nmea flight.fvc --verbose 2>&1 | tee conversion.log
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
            'timestamp': datetime.now().isoformat(),
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
- [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md) - Polars integration guide
- [/openwiki/operations/setup.md](/openwiki/operations/setup.md) - Setup and installation

---

## 🎯 Quick Reference

### Common Conversion Commands

```bash
# NMEA to .fvc
uv run fvc df --in flight.nmea convert nmea flight.fvc

# Safir MQTT to .fvc
uv run fvc df --in safir.jsonl convert safirmqtt flight.fvc

# DJI Datcon to .fvc
uv run fvc df --in flight.csv convert datcon flight.fvc

# Validate .fvc file
uv run fvc df --in flight.fvc validate

# Correlate two flight logs
uv run fvc df correlate flight1.fvc flight2.fvc --output correlated.fvc
```

### Conversion Quality Checklist

- [ ] Input file exists and is readable
- [ ] Format is correctly detected
- [ ] All required fields are present
- [ ] Metadata is correctly generated
- [ ] Data records are valid
- [ ] Output file is valid JSON-Lines
- [ ] Validation passes
- [ ] Performance is acceptable
- [ ] Documentation is updated

### Performance Checklist

- [ ] Uses Polars for data processing
- [ ] Processes in batches for large files
- [ ] Drops unused columns
- [ ] Uses lazy evaluation where appropriate
- [ ] Memory usage is monitored
- [ ] Query performance is tracked

---

**Next Steps:**

- 📖 Read [/openwiki/workflows/validation.md](/openwiki/workflows/validation.md) for validation workflows
- ⚡ Learn about [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md) for performance optimizations
- 🔄 Explore [/openwiki/operations/development.md](/openwiki/operations/development.md) for development best practices
