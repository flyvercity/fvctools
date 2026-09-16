---
type: Development Guide
title: Development Practices and Guidelines

description: Best practices, coding standards, type hints, performance tips, testing strategies, and contribution workflows for developing fvctools

tags: [development, practices, standards, workflows, contributing, python, fvctools]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T12:24:16.401Z
sources:
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-3dd122e5fe934502061804bf
    resource: repo://src/fvc/tools/calc/cli.py
  - id: openwiki-source-d89fcd3fc5cba86004bd8f31
    resource: repo://src/fvc/tools/cli.py
  - id: openwiki-source-5ed15730fa37741e976035a2
    resource: repo://src/fvc/tools/df/cli.py
  - id: openwiki-source-e1ac5460a2f3e3c6f12f34a1
    resource: repo://src/fvc/tools/df/core.py
  - id: openwiki-source-fc5776122634f6b1b77cbd0c
    resource: repo://src/fvc/tools/df/schema.yaml
  - id: openwiki-source-42662411323116374c280235
    resource: repo://src/fvc/tools/df/xformats/agentfly.py
  - id: openwiki-source-79d703d62c9bb8dd3287cb65
    resource: repo://src/fvc/tools/df/xformats/datcon.py
  - id: openwiki-source-4ac6699f79ea2f0f545f3b19
    resource: repo://src/fvc/tools/df/xformats/nmea.py
  - id: openwiki-source-3e82d7ecdef56423054c4cab
    resource: repo://src/fvc/tools/df/xformats/senhive.py
  - id: openwiki-source-5e1b07b7b3c0fa28410ec278
    resource: repo://src/fvc/tools/df/xformats/ulog.py
  - id: openwiki-source-e8dbd945884f7fd08dd33282
    resource: repo://src/fvc/tools/render/cli.py
  - id: openwiki-source-9187f334bf5708864726b986
    resource: repo://tests/test_datcon_xformat.py
  - id: openwiki-source-61b3f15c183440d72d1ba780
    resource: repo://tests/test_nmea_xformat.py
  - id: openwiki-source-1ca82fe21babf2652db08db1
    resource: repo://tests/test_ulog_xformat.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T12:24:16.401Z" }
---

# Development Practices and Guidelines

This guide provides best practices, coding standards, and development workflows for contributing to **fvctools**, the Flyvercity CLI Tools Suite.

## Overview

fvctools is a modular Python-based CLI suite designed for processing, conversion, and validation of geospatial aviation data. The project follows modern Python development practices with a focus on:

- **Type hints** for better code clarity and IDE support
- **Ruff** for linting and formatting
- **Pre-commit hooks** for code quality
- **Comprehensive testing** with pytest
- **Documentation-first approach**
- **Modular architecture** for maintainability
- **Performance optimization** for large datasets

## Development Principles

### 1. Code Quality

- ✅ **Type hints** for all functions and methods
- ✅ **Descriptive variable names** (avoid abbreviations)
- ✅ **Consistent formatting** (Ruff with 120 character line length)
- ✅ **Clear documentation** (docstrings, comments, module help)
- ✅ **Follow PEP 8** guidelines with Ruff's stricter rules
- ✅ **Use logging** for debugging and monitoring
- ✅ **Validate inputs** early

### 2. Performance

- ✅ **Use Polars** for data processing (when applicable)
- ✅ **Lazy evaluation** for memory efficiency
- ✅ **Avoid premature optimization** (profile first)
- ✅ **Parallel processing** where beneficial
- ✅ **Streaming where possible** for large files
- ✅ **Optimize I/O operations** (buffered reading/writing)
- ✅ **Use efficient data structures** (arrays, generators)

### 3. Maintainability

- ✅ **Modular design** (separate concerns)
- ✅ **Single responsibility principle**
- ✅ **Clear function boundaries**
- ✅ **Avoid global state**
- ✅ **Use configuration** for runtime parameters
- ✅ **Write reusable code** (helper functions, utilities)
- ✅ **Keep functions small** (< 50 lines)

### 4. Testing

- ✅ **Unit tests** for individual components
- ✅ **Integration tests** for component interactions
- ✅ **Performance tests** for critical paths
- ✅ **Test edge cases** (nulls, errors, boundaries)
- ✅ **High test coverage** (>80% overall)
- ✅ **Property-based testing** for validation logic
- ✅ **Mock external dependencies**

### 5. Documentation

- ✅ **Docstrings** for all public functions (Google style)
- ✅ **Type hints** for IDE support
- ✅ **Architecture documentation** for complex components
- ✅ **Workflow guides** for common tasks
- ✅ **Update docs with code changes**
- ✅ **Module help functions** for format-specific documentation
- ✅ **Schema documentation** for data formats

## Architecture Overview

fvctools follows a **modular architecture** with clear separation of concerns:

```
src/fvc/
├── __init__.py              # Package initialization
├── tools/
│   ├── __init__.py
│   ├── cli.py               # Main CLI entry point
│   ├── df/                  # Data File tools
│   │   ├── __init__.py
│   │   ├── cli.py           # df CLI commands
│   │   ├── core.py          # Core conversion/validation logic
│   │   ├── metadata.py      # METADATA handling
│   │   ├── schema.py        # Schema validation
│   │   ├── correlate.py     # Correlation engine
│   │   ├── fusion.py        # Fusion operations
│   │   ├── utils.py         # Shared utilities
│   │   └── xformats/        # Format converters
│   │       ├── __init__.py
│   │       ├── base.py      # Base converter pattern (not used directly)
│   │       ├── nmea.py      # NMEA converter
│   │       ├── ulog.py      # ULog converter
│   │       ├── agentfly.py  # AgentFly converter
│   │       ├── datcon.py    # DatCon converter
│   │       ├── senhive.py   # SenHive converter
│   │       ├── ...          # Other format converters
│   ├── calc/                # Geospatial calculations
│   │   ├── __init__.py
│   │   ├── cli.py           # calc CLI
│   │   ├── geoid.py         # Geoid calculations
│   │   └── terrain.py       # Terrain calculations
│   ├── render/              # Visualization tools
│   │   ├── __init__.py
│   │   ├── cli.py           # render CLI
│   │   └── core.py          # Rendering engine
│   ├── flightlog/           # Flight log specific tools
│   │   └── cli.py
│   └── utils.py             # Shared utilities
└── __main__.py             # Module entry point
```

### Core Conversion Pattern

fvctools uses a **converter function pattern** rather than a class hierarchy:

```python
# Each format has a convert_to_fvc() function
def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    """Convert external format to FVC format"""
    # Implementation here
```

**Example: NMEA Converter**

```python
# src/fvc/tools/df/xformats/nmea.py

def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    """
    Convert NMEA log to FVC flightlog format.
    
    Requires base-date parameter for timestamp calculation.
    """
    base_date = extract_base_date(params)
    
    # Update metadata
    metadata.update({
        'content': 'flightlog',
        'source': 'nmea',
        'base-date': base_date.date().isoformat(),
    })
    
    output.write(metadata)
    
    # Process NMEA sentences
    for message in iterate_nmea_file(input_path, message_types=['GGA']):
        if not isinstance(message, pynmea2.GGA):
            continue
            
        timestamp = datetime.combine(base_date, message.timestamp, tzinfo=UTC)
        record = create_flight_record(message, timestamp)
        output.write(record)
```

### CLI Architecture

fvctools uses **Click** for CLI with a hierarchical command structure:

```python
# src/fvc/tools/cli.py

@click.group(help='Flyvercity CLI Tools Suite')
def cli():
    """Main CLI entry point"""
    pass

@cli.group(help='Data file conversion and manipulation tool')
def df():
    """Data File tools group"""
    pass

@df.command(name='convert')
def convert_command():
    """Convert external format to FVC"""
    pass

@df.command(name='validate')
def validate_command():
    """Validate FVC file against schema"""
    pass
```

**Available CLI Commands:**

```bash
# Main commands
fvc df convert <format> [output]  # Convert to FVC format
fvc df validate                   # Validate FVC file
fvc df correlate <files>          # Correlate multiple files
fvc calc <command>                # Geospatial calculations
fvc render <command>              # Generate visualizations
```

## Coding Standards

### 1. Python Style Guide

Follow **PEP 8** with Ruff's stricter rules:

```python
# ✅ Good: Consistent indentation (4 spaces)
for i in range(10):
    print(i)

# ✅ Good: Descriptive names (avoid abbreviations)
flight_data = load_flight_data()

# ✅ Good: Type hints for all functions
from typing import List, Optional, TypedDict

def process_flight(
    flight_id: str,
    start_time: Optional[int] = None
) -> List[FlightRecord]:
    ...

# ✅ Good: Line length up to 120 characters (Ruff config)
long_variable_name = calculate_derived_field(value1, value2, value3)

# ✅ Good: Consistent quotes (Ruff: single quotes)
metadata = {'content': 'flightlog', 'source': 'nmea'}

# ✅ Good: Use context managers for resources
with open("file.json", "r") as f:
    data = json.load(f)
```

### 2. Type Hints

Use **Python 3.12+ type hints** with full coverage:

```python
# ✅ Good: Basic types
from typing import List, Dict, Optional, Union

def process_file(input_path: str, output_path: str) -> bool:
    ...

# ✅ Good: Complex types with TypedDict
from typing import TypedDict

class FlightRecord(TypedDict):
    time: int
    lat: float
    lon: float
    alt: float

def load_flight_data(path: str) -> List[FlightRecord]:
    ...

# ✅ Good: Use Optional for nullable values
def get_altitude(record: FlightRecord) -> Optional[float]:
    return record.get("alt")

# ✅ Good: Use Union for multiple types
def parse_value(value: Union[str, int, float]) -> float:
    ...

# ✅ Good: Use TypeAlias for complex types
from typing import TypeAlias

Position: TypeAlias = Dict[str, float]
FlightData: TypeAlias = Dict[str, Union[int, Position]]
```

### 3. Error Handling

```python
# ✅ Good: Specific exceptions with logging
import logging
logger = logging.getLogger(__name__)

try:
    data = load_data()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}", exc_info=True)
    raise

# ✅ Good: Validate inputs early
def process_flight(flight_id: str) -> FlightData:
    if not flight_id:
        raise ValueError("flight_id cannot be empty")
    if len(flight_id) > 50:
        raise ValueError("flight_id too long")
    ...

# ✅ Good: Return None or raise exception (be consistent)
def find_flight(flight_id: str) -> Optional[FlightData]:
    if flight_id in flights:
        return flights[flight_id]
    return None

# ❌ Bad: Bare except
try:
    ...
except:
    pass

# ❌ Bad: Swallowing exceptions silently
except Exception:
    logger.warning("Something happened")
```

### 4. Logging

```python
import logging

# ✅ Good: Get logger per module
logger = logging.getLogger(__name__)

# ✅ Good: Different log levels
logger.debug("Processing file: %s", file_path)
logger.info("Converted %d records", record_count)
logger.warning("Missing optional field: %s", field_name)
logger.error("Failed to process file: %s", error)
logger.critical("Critical failure: %s", error)

# ✅ Good: Structured logging with context
logger.info(
    "File processed",
    extra={
        "file": file_path,
        "records": record_count,
        "duration_ms": duration * 1000,
        "success": True
    }
)

# ✅ Good: Conditional verbose logging
if verbose:
    logger.debug("Detailed processing information")
```

### 5. Configuration

```python
import os
from typing import Optional

# ✅ Good: Environment variables with defaults
def get_config() -> dict:
    return {
        "data_dir": os.getenv("FVC_DATA_DIR", "/data"),
        "log_level": os.getenv("FVC_LOG_LEVEL", "INFO"),
        "validate_strict": os.getenv("FVC_VALIDATE_STRICT", "false") == "true",
        "cache_dir": os.getenv("FVC_CACHE", None),
    }

# ✅ Good: Configuration class for complex setups
class AppConfig:
    def __init__(self):
        self.data_dir = Path(os.getenv("FVC_DATA_DIR", "/data"))
        self.max_file_size = int(os.getenv("FVC_MAX_FILE_SIZE", "1000000"))
        self.parallel = os.getenv("FVC_PARALLEL", "true") == "true"
        self.egm_file = os.getenv("FVC_EGM_FILE")

# ✅ Good: Use benedict for nested configuration
from benedict import benedict

config = benedict({
    "aws": {
        "profile": os.getenv("AWS_PROFILE"),
        "region": os.getenv("AWS_REGION", "us-east-1")
    }
})
```

## Performance Best Practices

### 1. Use Polars for Data Processing

```python
# ✅ Good: Use Polars for large datasets
import polars as pl

df = pl.read_csv("large_file.csv")
result = df.filter(pl.col("alt") > 100.0).collect()

# ✅ Good: Use lazy evaluation for optimization
lazy_df = df.lazy()
result = lazy_df.filter(...).collect()

# ✅ Good: Use appropriate data types
pl.Int32()  # Instead of Int64 for timestamps
pl.Float32()  # Instead of Float64 for coordinates

# ✅ Good: Use Polars expressions for complex operations
df.with_columns(
    (pl.col("lat") * 100).alias("lat_scaled"),
    (pl.col("alt") - pl.col("base_alt")).alias("rel_alt")
).filter(pl.col("time") > start_time)
```

### 2. Streaming Processing

```python
# ✅ Good: Stream large files with context managers
with open("large_file.jsonl", "r") as f:
    for line in f:
        record = json.loads(line)
        process_record(record)

# ✅ Good: Use generators for memory efficiency
def read_large_file(file_path: str):
    with open(file_path, "r") as f:
        for line in f:
            yield json.loads(line)

# Process records one at a time
for record in read_large_file("large_file.jsonl"):
    process_record(record)

# ✅ Good: Use JsonlinesIO for FVC format
def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    # Write metadata
    output.write(metadata)
    
    # Stream records
    for record in process_records(input_path):
        output.write(record)
```

### 3. Parallel Processing

```python
# ✅ Good: Use Polars parallel operations
import polars as pl

df = pl.DataFrame(...)
result = df.group_by("flight_id").agg(...).collect()  # Parallelized

# ✅ Good: Use GNU parallel for batch processing
find ./input -name "*.nmea" | parallel -j $(nproc) process_file {}

# ✅ Good: Use multiprocessing for CPU-bound tasks
from multiprocessing import Pool

with Pool() as pool:
    results = pool.map(process_file, file_list)

# ✅ Good: Use threading for I/O-bound tasks
import threading

threads = []
for file in files:
    thread = threading.Thread(target=process_file, args=(file,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
```

### 4. Memory Management

```python
# ✅ Good: Filter early to reduce memory usage
lazy_df.filter(pl.col("time") > start_time).collect()

# ✅ Good: Process in chunks
chunk_size = 10000
for chunk in df.iter_slices(chunk_size):
    process_chunk(chunk)

# ✅ Good: Use efficient data structures
import array

latitudes = array.array('d')  # Double precision
longitudes = array.array('d')

# ✅ Good: Clear references when done
large_object = process_data()
result = compute_result(large_object)
del large_object  # Explicit cleanup
```

### 5. Caching

```python
# ✅ Good: Cache expensive operations with LRU cache
import functools

@functools.lru_cache(maxsize=1000)
def get_geoid_undulation(lat: float, lon: float) -> float:
    """Cache geoid undulation calculations"""
    return calculate_undulation(lat, lon)

# ✅ Good: Cache DataFrame operations
cached_df = df.lazy().filter(...).collect()

# ❌ Bad: Cache large objects that consume memory
@functools.lru_cache(maxsize=100)
def get_large_dataset() -> pl.DataFrame:
    return pl.read_csv("huge_file.csv")  # Don't do this!
```

### 6. Optimized I/O

```python
# ✅ Good: Use buffered reading for large files
with open("large_file.nmea", "r", buffering=8192) as f:
    for line in f:
        process_line(line)

# ✅ Good: Use Path for efficient file operations
from pathlib import Path

input_path = Path("input.nmea")
if input_path.exists() and input_path.stat().st_size > MAX_SIZE:
    process_large_file(input_path)

# ✅ Good: Use memory-mapped files for binary data
import mmap

with open("data.bin", "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)
    # Access data via mm
```

### 7. Performance Optimizations in fvctools

fvctools includes several performance optimizations:

**Fast NMEA Parsing:**
```python
# src/fvc/tools/df/xformats/nmea.py
def iterate_nmea_file(input_path: Path, strict: bool = False, message_types: list[str] | None = None):
    with input_path.open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # ⚡ Bolt: Fast string check to skip expensive pynmea2.parse() for irrelevant lines
            # This can yield ~2x speedup when many message types are present in the log
            if message_types is not None:
                header = line.split(',', 1)[0]
                if not any(header.endswith(message_type) for message_type in message_types):
                    continue
            
            try:
                message = pynmea2.parse(line)
            except pynmea2.ParseError as e:
                if strict:
                    raise ValueError(f'Unable to parse line {line_no}') from e
                lg.warning(f'Unable to parse line {line_no}')
                continue
            
            yield message
```

**Efficient Schema Validation:**
```python
# src/fvc/tools/df/core.py
# ⚡ Bolt: Create the validator once to avoid recompilation overhead for each record
# This significantly improves performance for large files.
cls = jsonschema.validators.validator_for(content_schema)
cls.check_schema(content_schema)
validator = cls(content_schema)

for data in f.iterate():
    try:
        validator.validate(data)
    except Exception as e:
        lg.error(f'Validation error at line {f.in_line_no()}: {e}')
        error_count += 1
```

## Testing Best Practices

### 1. Test Structure

```
tests/
├── conftest.py               # Test fixtures
├── test_agentfly_xformat.py  # AgentFly format tests
├── test_datcon_xformat.py    # DatCon format tests
├── test_nmea_xformat.py      # NMEA format tests
├── test_senhive_xformat.py   # SenHive format tests
├── test_ulog_xformat.py      # ULog format tests
├── test_render_core.py       # Rendering tests
├── test_segment.py           # Segment operations tests
├── test_utils.py             # Utility function tests
└── verify_ps_security.py     # Security verification tests
```

### 2. Test Fixtures

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
    """Sample NMEA data for testing"""
    return """$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46
$GNRMC,123456.78,A,5234.1234,N,00450.1234,E,6.1,45.0,010123,0.0,E,A*1C"""

@pytest.fixture
def sample_flight():
    """Sample flight data in .fvc format"""
    return """{"content": "flightlog", "source": "nmea", "origin": "test.log"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}}
{"time": {"unix": 1756033206883}, "pos": {"loc": {"lat": 52.3001, "lon": 4.9001, "alt": 100.8}}}"""

@pytest.fixture
def config():
    """Default configuration for tests"""
    return {
        "data_dir": "/tmp/test",
        "log_level": "DEBUG",
        "validate_strict": False,
    }
```

### 3. Writing Tests

**Example: NMEA Format Test**

```python
# tests/test_nmea_xformat.py

from unittest.mock import patch
from fvc.tools.df.xformats.nmea import iterate_nmea_file


def test_iterate_nmea_file_filters_on_header_only(temp_dir):
    """Test that message type filtering works correctly"""
    input_path = temp_dir / 'test.nmea'
    input_path.write_text('$GPRMC,contains-GGA*00\n', encoding='utf-8')

    # When filtering for GGA messages, RMC-only lines should be skipped
    messages = list(iterate_nmea_file(input_path, message_types=['GGA']))
    assert messages == []


def test_nmea_conversion_with_base_date(temp_dir):
    """Test NMEA to FVC conversion with base date parameter"""
    input_path = temp_dir / 'test.nmea'
    input_path.write_text('$GPGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46\n',
                         encoding='utf-8')
    
    # This test would use the actual convert_to_fvc function
    # with appropriate params including base-date
```

**Example: Converter Test**

```python
# tests/test_datcon_xformat.py

import pytest
from pathlib import Path
from fvc.tools.df.xformats.datcon import convert_to_fvc
from fvc.tools.df.utils import JsonlinesIO


def test_datcon_converter(temp_dir):
    """Test DatCon format conversion"""
    # Create test input file
    input_path = temp_dir / 'test.Dat'
    input_path.write_text("Sample DatCon data...")
    
    # Create output file
    output_path = temp_dir / 'output.fvc'
    
    # Create metadata
    metadata = {
        'content': 'flightlog',
        'source': 'datcon',
        'origin': str(input_path),
    }
    
    # Create params
    params = {
        'custom': [],
    }
    
    # Convert
    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc(params, metadata, input_path, output)
    
    # Assert
    assert output_path.exists()
    lines = output_path.read_text().strip().split('\n')
    assert len(lines) >= 1  # At least metadata
```

### 4. Test Coverage

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_nmea_xformat.py

# Run tests with coverage
pytest --cov=src/fvc --cov-report=html

# Run tests with coverage report
pytest --cov=src/fvc --cov-report=term-missing

# Run tests in watch mode (if using pytest-watch)
ptw

# Check test coverage requirements
# Aim for: >80% overall coverage
#          100% coverage for critical paths
#          Tests for edge cases and error handling
```

**Coverage Reporting:**

```python
# .coveragerc (if exists)
[run]
source = src/fvc
omit = 
    */__init__.py
    */tests/*
    */conftest.py

[report]
exclude_lines = 
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    @abstractmethod
```

### 5. Property-Based Testing

```python
# tests/test_properties.py

import pytest
import hypothesis.strategies as st
from hypothesis import given
from fvc.tools.df.schema import SchemaValidator


@given(st.floats(min_value=-90, max_value=90))
def test_latitude_range(lat):
    """Test that latitude values are in valid range [-90, 90]"""
    assert -90 <= lat <= 90


@given(st.integers(min_value=0, max_value=2000000000))
def test_unix_timestamp(timestamp):
    """Test that Unix timestamps are reasonable"""
    # 2038 problem check
    assert timestamp < 2**31


@given(st.lists(st.text(min_size=1, max_size=100)))
def test_non_empty_strings(strings):
    """Test that non-empty strings are handled correctly"""
    for s in strings:
        assert len(s) > 0
```

### 6. Integration Testing

```python
# tests/test_conversion_pipeline.py

import pytest
from pathlib import Path


def test_full_conversion_pipeline(temp_dir):
    """Test end-to-end conversion pipeline"""
    # 1. Create test input file
    input_file = temp_dir / 'flight.nmea'
    input_file.write_text("$GPGGA,...\n")
    
    # 2. Convert to FVC
    output_file = temp_dir / 'flight.fvc'
    result = convert_file(input_file, output_file, 'nmea')
    
    # 3. Validate output
    assert result is True
    assert output_file.exists()
    
    # 4. Validate against schema
    validation_result = validate_file(output_file)
    assert validation_result is True
```

## Development Workflow

### 1. Git Workflow

fvctools uses **GitHub flow**:

```
main (protected)
  │
  ├─ feature/<scope>/<description> (branch)
  │   ├─ commit 1: Add feature
  │   ├─ commit 2: Fix bug
  │   └─ commit 3: Update docs
  │
  └─ Pull Request → main
        │
        ├─ Code review
        ├─ CI checks
        └─ Merge
```

**Branch naming conventions:**
- `feature/df-nmea-optimization` - New features
- `fix/df-validation-error` - Bug fixes
- `refactor/df-core` - Code refactoring
- `docs/df-readme` - Documentation updates
- `perf/df-conversion-speed` - Performance improvements
- `test/df-coverage` - Test additions

### 2. Commit Messages

Follow **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]

# Examples:
feat(df): add NMEA converter optimization
fix(core): handle null values in conversion
refactor(df): simplify METADATA validation
perf(df): improve NMEA parsing speed by 2x
docs(schema): update FLIGHTLOG schema documentation
test(nmea): add edge case tests for GGA parsing
chore(deps): update dependencies to latest versions
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

**Scopes (examples):**
- `df`: Data File tools
- `calc`: Geospatial calculations
- `render`: Visualization tools
- `core`: Core functionality
- `nmea`: NMEA format converter
- `ulog`: ULog format converter
- `schema`: Schema validation
- `cli`: Command-line interface

### 3. Pre-commit Hooks

fvctools uses **pre-commit** for code quality:

```bash
# Install hooks (run once)
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

**Configured hooks:**
- **ruff**: Linting and formatting (line length: 120)
- **mypy**: Type checking
- **check-toml**: TOML file validation
- **check-yaml**: YAML file validation
- **end-of-file-fixer**: Ensure files end with newline
- **trailing-whitespace**: Remove trailing whitespace
- **pyupgrade**: Upgrade syntax to latest Python version

**Configuration:**

```yaml
# .pre-commit-config.yaml (if exists)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    hooks:
      - id: ruff
        args: [--fix, --show-fixes]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.1
    hooks:
      - id: mypy
        additional_dependencies: [types-jsonschema, types-python-dateutil]
```

### 4. Code Review Process

**Before submitting a PR:**

1. ✅ Run pre-commit hooks: `pre-commit run --all-files`
2. ✅ Run tests: `pytest`
3. ✅ Check type hints: `ruff check src/fvc`
4. ✅ Format code: `ruff format src/fvc`
5. ✅ Update documentation
6. ✅ Add tests for new functionality
7. ✅ Update CHANGELOG if applicable
8. ✅ Verify no new warnings or errors

**PR checklist:**
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] No new warnings
- [ ] Performance acceptable
- [ ] Security considerations addressed
- [ ] Follows Conventional Commits
- [ ] Branch name follows convention

**Review process:**
1. Self-review your changes
2. Request review from at least 2 team members
3. Address review comments
4. Update tests if needed
5. Re-request review
6. Merge after approvals

### 5. Testing Workflow

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_nmea_xformat.py

# Run tests with coverage
pytest --cov=src/fvc --cov-report=html

# Run tests with coverage report
pytest --cov=src/fvc --cov-report=term-missing

# Run tests in verbose mode
pytest -v

# Run tests with specific marker
pytest -m "slow"

# Run tests and show output
pytest -s

# Check for test failures only
pytest --tb=no -q
```

**Test markers:**
```python
# In conftest.py or test files
import pytest

pytestmark = pytest.mark.slow  # Mark all tests in file as slow

@pytest.mark.integration
def test_integration():
    """Integration test"""
    ...

@pytest.mark.performance
def test_performance():
    """Performance test"""
    ...
```

## Module Help System

fvctools includes a **module help system** for format-specific documentation:

```python
# Each format module can define a module_help() function
def module_help():
    """Return help text for format-specific parameters"""
    return '- base-date=<datestring> is required for this format'
```

**Usage:**

```bash
# Show help for a specific format
fvc df help nmea

# Example output:
Help for 'nmea' additional parameters:
- base-date=<datestring> is required for this format
```

**Available formats with help:**
- `nmea`: Requires `base-date` parameter
- `agentfly`: Custom parameters for AgentFly logs
- `datcon`: Custom parameters for DatCon logs
- `senhive`: Custom parameters for SenHive logs

## Debugging and Profiling

### 1. Debugging Techniques

```python
# ✅ Good: Use logging with appropriate levels
import logging
logger = logging.getLogger(__name__)

logger.debug("Processing record: %s", record)
logger.info("Processing %d records", record_count)
logger.warning("Missing optional field: %s", field_name)
logger.error("Failed to process file: %s", error)

# ✅ Good: Use pdb for interactive debugging
import pdb; pdb.set_trace()

# ✅ Good: Use IDE debugger (VS Code, PyCharm)
# Set breakpoints in your IDE

# ✅ Good: Print intermediate values for quick debugging
print(f"DEBUG: df shape = {df.shape}")
print(f"DEBUG: records = {len(df)}")

# ✅ Good: Use rich for pretty printing
from rich import print
print("[bold green]Success![/bold green]")
print_json(data=metadata)
```

### 2. Profiling Performance

```python
# ✅ Good: Use cProfile for profiling
import cProfile

pr = cProfile.Profile()
pr.enable()

# Your code here
result = convert("input.nmea", "output.fvc")

pr.disable()
pr.print_stats(sort="cumtime")  # Sort by cumulative time

# ✅ Good: Use timeit for microbenchmarks
import timeit

time = timeit.timeit(
    "convert('input.nmea', 'output.fvc')",
    setup="from fvc.tools.df.xformats.nmea import convert_to_fvc; converter = NMEAConverter()",
    number=10
)
print(f"Average time: {time / 10:.4f}s")

# ✅ Good: Use memory_profiler for memory usage
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Your code here
    ...

# Run with:
mprof run python script.py
mprof plot
```

### 3. Common Debugging Scenarios

**Issue**: Conversion fails silently

```python
# Add debug logging
logger.setLevel(logging.DEBUG)

# Add try-except with logging
try:
    converter.convert(input_path, output_path)
except Exception as e:
    logger.error("Conversion failed: %s", e, exc_info=True)
    raise

# Check file permissions
import os
logger.debug("Output file permissions: %s", oct(os.stat(output_path).st_mode))
```

**Issue**: Performance is slow

```python
# Profile the code
pr = cProfile.Profile()
pr.enable()

result = converter.convert(input_path, output_path)

pr.disable()
pr.print_stats(sort="cumtime")

# Check for bottlenecks
# - File I/O operations
# - Data processing loops
# - Memory allocations
# - External API calls
```

**Issue**: Validation fails

```python
# Use verbose validation
validator = SchemaValidator()
success = validator.validate_file("output.fvc", verbose=True)

# Check METADATA
with open("output.fvc", "r") as f:
    metadata = json.loads(f.readline())
    print(f"METADATA: {metadata}")

# Check data records
for line_num, line in enumerate(f, start=2):
    try:
        record = json.loads(line)
        print(f"Record {line_num}: {record}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON at line {line_num}: {e}")
```

### 4. Debug CLI Commands

```bash
# Run with verbose logging
fvc --verbose df convert nmea output.fvc

# Run with debug logging
fvc --verbose df validate input.fvc

# Check environment variables
fvc --verbose df convert nmea output.fvc --custom base-date=2024-01-01

# Use rich console for better output
fvc --json df convert nmea output.fvc
```

## Security Best Practices

### 1. Input Validation

```python
# ✅ Good: Validate file paths to prevent path traversal
import os

def safe_path(base_dir: str, relative_path: str) -> str:
    """Ensure path is within base directory"""
    full_path = os.path.abspath(os.path.join(base_dir, relative_path))
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Path traversal detected")
    return full_path

# ✅ Good: Validate file extensions
import os

def allowed_extension(filename: str) -> bool:
    return filename.lower().endswith((".nmea", ".ulg", ".json", ".fvc", ".csv"))

# ✅ Good: Sanitize inputs
import re

def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

# ✅ Good: Validate CLI arguments
import click

@click.argument('x_format', type=click.Choice(["nmea", "ulog", "agentfly", "datcon"]))
def convert_command(x_format):
    # x_format is guaranteed to be one of the allowed values
    ...
```

### 2. Error Messages

```python
# ✅ Good: Generic error messages (don't reveal system details)
raise ValueError("Invalid input format")

# ❌ Bad: Reveal system details
raise ValueError(f"File {file_path} not found on system /home/user/data")

# ✅ Good: Log errors with full details, return user-friendly messages
try:
    process_file(file_path)
except FileNotFoundError as e:
    logger.error("File not found: %s", file_path, exc_info=True)
    raise ValueError("Input file not found. Please check the file path.")
```

### 3. Credential Management

```python
# ✅ Good: Use environment variables
import os

aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

# ✅ Good: Use AWS credentials file
# ~/.aws/credentials

# ✅ Good: Use IAM roles (for EC2, ECS)
# No credentials needed - use instance role

# ✅ Good: Use AWS profile with boto3
import boto3

session = boto3.Session(profile_name="my-profile")
s3 = session.client("s3")

# ❌ Bad: Hardcode credentials
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "secret..."
```

### 4. File Permissions

```python
# ✅ Good: Set appropriate file permissions
import os

os.chmod("output.fvc", 0o644)  # Read/write for owner, read for others

# ✅ Good: Use umask
os.umask(0o022)  # Default: 644 for files, 755 for directories

# ✅ Good: Run as non-root user
import getpass

if getpass.getuser() == "root":
    raise RuntimeError("Do not run as root")

# ✅ Good: Validate input file permissions before processing
input_path = Path(params['input_path'])
if not input_path.exists():
    raise FileNotFoundError(f"Input file not found: {input_path}")
if not input_path.is_file():
    raise ValueError(f"Input path is not a file: {input_path}")
```

### 5. Dependency Security

```python
# ✅ Good: Pin dependency versions in pyproject.toml
[project]
dependencies = [
    "pyparsing>=3.2.0,<4.0.0",
    "toolz>=1.0.0,<2.0.0",
    "jsonschema>=4.23.0,<5.0.0",
]

# ✅ Good: Use dependency groups for dev vs prod
[dependency-groups]
dev = [
    "duct>=1.0.1",
    "pytest>=9.0.2",
    "ruff>=0.14.0",
]

# ✅ Good: Regularly update dependencies
# Use dependabot or similar tools

# ✅ Good: Verify dependencies before installation
uv pip install --dry-run -e .
```

## Continuous Integration

### 1. GitHub Actions Workflow

fvctools uses GitHub Actions for CI/CD:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install uv
          uv pip install -e ".[dev]"
      
      - name: Run pre-commit hooks
        run: pre-commit run --all-files
      
      - name: Run tests
        run: pytest
      
      - name: Check types
        run: mypy src/fvc
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### 2. Test Matrix

```yaml
# Test multiple Python versions
strategy:
  matrix:
    python-version: ["3.12", "3.13"]

# Test on multiple platforms
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### 3. Code Quality Checks

```yaml
- name: Lint with Ruff
  run: ruff check src/fvc

- name: Format check
  run: ruff format --check src/fvc

- name: Type checking
  run: mypy src/fvc

- name: Security scan
  run: bandit -r src/fvc

- name: Check dependencies
  run: uv pip check
```

### 4. Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install build tools
        run: pip install hatch
      
      - name: Build package
        run: hatch build
      
      - name: Publish to PyPI
        run: hatch publish
        env:
          HATCH_INDEX_USER: __token__
          HATCH_INDEX_AUTH: ${{ secrets.PYPI_API_TOKEN }}
```

## Release Process

### 1. Versioning

fvctools uses **semantic versioning** with year-based major/minor:

```
YYYY.MM.PATCH

Examples:
- 2026.5.12 - Version from pyproject.toml
- 1.0.0 - First stable release
- 2026.6.0 - New features
- 2026.5.13 - Bug fix
```

**Version components:**
- `YYYY`: Year of release
- `MM`: Month of release
- `PATCH`: Patch number (incremental fixes)

### 2. Changelog

Maintain a `CHANGELOG.md` with the following structure:

```markdown
# Changelog

## [2026.5.12] - 2026-05-12

### Added
- Polars integration for AgentFly, DatCon, and SenHive converters
- Performance optimizations for format converters
- New format converters: agentfly, datcon, senhive

### Changed
- Updated schema validation to be more strict
- Improved error messages
- Refactored metadata handling

### Fixed
- NMEA parser handling of edge cases
- ULog conversion for certain message types
- Schema validation for nested fields

## [2026.4.0] - 2026-04-01

### Added
- Initial release of fvctools
- NMEA, ULog, SAFIR MQTT converters
- Flight log validation
- Interactive visualization
```

### 3. Release Steps

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): prepare version 2026.5.12"

# 4. Create tag
git tag -a v2026.5.12 -m "Version 2026.5.12"

# 5. Push to remote
git push origin main
git push origin v2026.5.12

# 6. Create GitHub release
# Go to GitHub → Releases → Draft new release
# Tag: v2026.5.12
# Title: Version 2026.5.12
# Description: Copy from CHANGELOG.md

# 7. Publish to PyPI
uv pip install hatch
python -m hatch publish
```

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Architecture Overview](/openwiki/architecture/overview.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Setup Guide](/openwiki/operations/setup.md)
- [Testing Guide](/openwiki/testing/overview.md)
- [Integration Guides](/openwiki/integrations/index.md)
- [Data Format Schema](/openwiki/architecture/data-formats.md)

## Quick Reference

| Task | Command/Tool |
|------|--------------|
| Format code | `ruff format src/fvc` |
| Lint code | `ruff check src/fvc` |
| Run tests | `pytest` |
| Type check | `mypy src/fvc` |
| Pre-commit | `pre-commit run --all-files` |
| Profile code | `python -m cProfile -s cumtime script.py` |
| Generate docs | `python scripts/generate_schema_docs.py` |
| Install dev dependencies | `uv pip install -e ".[dev]"` |
| Run CLI | `uv run fvc df convert nmea output.fvc` |

## Best Practices Summary

✅ **Write type hints** for all functions
✅ **Use pre-commit hooks** before committing
✅ **Write tests** for new functionality
✅ **Update documentation** with code changes
✅ **Follow PEP 8** with Ruff's stricter rules (120 chars)
✅ **Use logging** for debugging and monitoring
✅ **Validate inputs** early
✅ **Handle errors gracefully**
✅ **Profile performance** before optimizing
✅ **Keep commits small and focused**
✅ **Write good commit messages** (Conventional Commits)
✅ **Review your own PRs** before requesting review
✅ **Update CHANGELOG** for releases
✅ **Use Polars** for data processing when applicable
✅ **Stream files** instead of loading entirely into memory
✅ **Use generators** for memory efficiency
✅ **Cache expensive operations** judiciously
✅ **Test edge cases** (nulls, errors, boundaries)
✅ **Mock external dependencies** in tests

## Next Steps

- **Set up development environment**: [/openwiki/operations/setup.md](/openwiki/operations/setup.md)
- **Learn architecture**: [/openwiki/architecture/overview.md](/openwiki/architecture/overview.md)
- **Explore CLI tools**: [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md)
- **Write your first contribution**: Start with a bug fix or small feature
- **Check existing issues**: Look for `good-first-issue` labels
- **Join discussions**: Participate in design discussions
