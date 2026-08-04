---
type: Development Guide
title: Development Practices and Guidelines

description: Best practices, coding standards, and development workflows for contributing to fvctools
resource: /src/fvc

tags: [development, practices, standards, workflows, contributing]
---

# Development Practices and Guidelines

This guide provides best practices, coding standards, and development workflows for contributing to **fvctools**.

## Overview

fvctools follows modern Python development practices with:

- **Type hints** for better code clarity and IDE support
- **Ruff** for linting and formatting
- **Pre-commit hooks** for code quality
- **Comprehensive testing** with pytest
- **Documentation-first approach**
- **Modular architecture** for maintainability

## Development Principles

### 1. Code Quality

- ✅ **Type hints** for all functions and methods
- ✅ **Descriptive variable names** (avoid abbreviations)
- ✅ **Consistent formatting** (Ruff)
- ✅ **Clear documentation** (docstrings, comments)
- ✅ **Follow PEP 8** guidelines

### 2. Performance

- ✅ **Use Polars** for data processing (when applicable)
- ✅ **Lazy evaluation** for memory efficiency
- ✅ **Avoid premature optimization** (profile first)
- ✅ **Parallel processing** where beneficial
- ✅ **Streaming where possible** for large files

### 3. Maintainability

- ✅ **Modular design** (separate concerns)
- ✅ **Single responsibility principle**
- ✅ **Clear function boundaries**
- ✅ **Avoid global state**
- ✅ **Use configuration** for runtime parameters

### 4. Testing

- ✅ **Unit tests** for individual components
- ✅ **Integration tests** for component interactions
- ✅ **Performance tests** for critical paths
- ✅ **Test edge cases** (nulls, errors, boundaries)
- ✅ **High test coverage** (>80%)

### 5. Documentation

- ✅ **Docstrings** for all public functions
- ✅ **Type hints** for IDE support
- ✅ **Architecture documentation** for complex components
- ✅ **Workflow guides** for common tasks
- ✅ **Update docs with code changes**

## Coding Standards

### 1. Python Style Guide

Follow **PEP 8** with Ruff's stricter rules:

```python
# ✅ Good: Consistent indentation
for i in range(10):
    print(i)

# ✅ Good: Descriptive names
flight_data = load_flight_data()

# ✅ Good: Type hints
from typing import List, Optional

def process_flight(
    flight_id: str,
    start_time: Optional[int] = None
) -> List[FlightRecord]:
    ...

# ✅ Good: Line length (Ruff: 120 chars)
long_variable_name = calculate_derived_field(value1, value2, value3)

# ✅ Good: Consistent quotes (Ruff: single quotes)
metadata = {'content': 'flightlog', 'source': 'nmea'}
```

### 2. Type Hints

Use **Python 3.12+ type hints**:

```python
# ✅ Good: Basic types
from typing import List, Dict, Optional, Union

def process_file(input_path: str, output_path: str) -> bool:
    ...

# ✅ Good: Complex types
from typing import List, Dict, Optional, Union, TypedDict

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
```

### 3. Error Handling

```python
# ✅ Good: Specific exceptions
try:
    data = load_data()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise

# ✅ Good: Context managers for resources
with open("file.json", "r") as f:
    data = json.load(f)

# ✅ Good: Validate inputs early
def process_flight(flight_id: str) -> FlightData:
    if not flight_id:
        raise ValueError("flight_id cannot be empty")
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

# ✅ Good: Structured logging
logger.info(
    "File processed",
    extra={
        "file": file_path,
        "records": record_count,
        "duration_ms": duration * 1000
    }
)
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
    }

# ✅ Good: Configuration class
class Config:
    def __init__(self):
        self.data_dir = os.getenv("FVC_DATA_DIR", "/data")
        self.max_file_size = int(os.getenv("FVC_MAX_FILE_SIZE", "1000000"))
        self.parallel = os.getenv("FVC_PARALLEL", "true") == "true"
```

## Development Workflow

### 1. Git Workflow

fvctools uses **GitHub flow**:

```
main (protected)
  │
  ├─ feature/my-feature (branch)
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

**Branch naming**:
- `feature/xxx` - New features
- `fix/xxx` - Bug fixes
- `refactor/xxx` - Code refactoring
- `docs/xxx` - Documentation updates
- `perf/xxx` - Performance improvements

### 2. Commit Messages

Follow **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]

# Examples:
feat(df): add NMEA converter
fix(core): handle null values in conversion
refactor(metadata): simplify METADATA validation
docs(schema): update FLIGHTLOG schema documentation
test(nmea): add edge case tests
chore(deps): update dependencies
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### 3. Pre-commit Hooks

fvctools uses **pre-commit** for code quality:

```bash
# Install hooks (run once)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

**Hooks configured**:
- **ruff**: Linting and formatting
- **mypy**: Type checking (if configured)
- **pyright**: Type checking (alternative)
- **check-toml**: TOML file validation
- **check-yaml**: YAML file validation
- **end-of-file-fixer**: Ensure files end with newline
- **trailing-whitespace**: Remove trailing whitespace

### 4. Code Review Process

**Before submitting a PR**:

1. ✅ Run pre-commit hooks
2. ✅ Run tests: `pytest`
3. ✅ Check type hints: `ruff check`
4. ✅ Format code: `ruff format`
5. ✅ Update documentation
6. ✅ Add tests for new functionality
7. ✅ Update CHANGELOG if applicable

**PR checklist**:
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] No new warnings
- [ ] Performance acceptable
- [ ] Security considerations addressed

### 5. Testing Workflow

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_nmea_xformat.py

# Run with coverage
pytest --cov=src/fvc --cov-report=html

# Run tests in watch mode (if using pytest-watch)
ptw

# Check test coverage
coverage report -m
```

**Test structure**:
```
tests/
├── test_nmea_xformat.py      # NMEA format tests
├── test_ulog_xformat.py       # ULog format tests
├── test_conversion.py         # Conversion tests
├── test_validation.py         # Validation tests
├── test_cli.py                # CLI tests
└── conftest.py               # Test fixtures
```

## Architecture Patterns

### 1. Modular Design

fvctools follows **modular architecture**:

```
src/fvc/
├── __init__.py              # Package initialization
├── tools/
│   ├── __init__.py
│   ├── cli.py               # CLI entry point
│   ├── df/
│   │   ├── __init__.py
│   │   ├── cli.py           # df CLI
│   │   ├── core.py          # Core conversion logic
│   │   ├── schema.py        # Schema validation
│   │   ├── metadata.py      # METADATA handling
│   │   ├── correlate.py     # Correlation engine
│   │   ├── fusion.py        # Fusion operations
│   │   └── xformats/
│   │       ├── __init__.py
│   │       ├── base.py      # Base converter class
│   │       ├── nmea.py      # NMEA converter
│   │       ├── ulog.py      # ULog converter
│   │       └── ...          # Other format converters
│   ├── calc/
│   │   ├── __init__.py
│   │   ├── cli.py           # calc CLI
│   │   ├── geoid.py         # Geoid calculations
│   │   └── terrain.py       # Terrain calculations
│   └── render/
│       ├── __init__.py
│       ├── cli.py           # render CLI
│       ├── core.py          # Rendering engine
│       └── templates.py     # Template management
└── __main__.py             # Module entry point
```

### 2. Base Converter Pattern

All format converters inherit from `BaseConverter`:

```python
# src/fvc/tools/df/xformats/base.py

from abc import ABC, abstractmethod
from typing import Optional

class BaseConverter(ABC):
    """Base class for all format converters"""
    
    @abstractmethod
    def convert(self, input_path: str, output_path: str) -> bool:
        """Convert input file to .fvc format"""
        pass
    
    def _write_metadata(self, output_path: str, content: str, source: str, origin: str) -> None:
        """Write METADATA to output file"""
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

**Example converter**:

```python
# src/fvc/tools/df/xformats/nmea.py

from fvc.tools.df.xformats.base import BaseConverter
import pynmea2

class NMEAConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str) -> bool:
        # Write METADATA
        self._write_metadata(output_path, "flightlog", "nmea", input_path)
        
        # Parse NMEA sentences
        with open(input_path, "r") as f:
            for line in f:
                if line.startswith("$"):
                    msg = pynmea2.parse(line)
                    record = self._nmea_to_record(msg)
                    self._write_record(output_path, record)
        
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

### 3. CLI Pattern

fvctools uses **Click** for CLI:

```python
# src/fvc/tools/df/cli.py

import click
from fvc.tools.df.core import ConversionEngine

@click.group()
def df():
    """Data File Tools"""
    pass

@df.command()
@click.option("--in", "input_path", required=True, help="Input file path")
@click.argument("format", type=click.Choice(["nmea", "ulog", "safirmqtt", ...]))
@click.argument("output_path", type=click.Path())
def convert(input_path, format, output_path):
    """Convert external format to .fvc"""
    engine = ConversionEngine()
    success = engine.convert(input_path, format, output_path)
    if not success:
        raise click.ClickException("Conversion failed")

@df.command()
@click.option("--in", "input_path", required=True, help="Input file path")
@click.option("--verbose", is_flag=True, help="Verbose output")
def validate(input_path, verbose):
    """Validate .fvc file"""
    engine = ValidationEngine()
    success = engine.validate(input_path, verbose=verbose)
    if not success:
        raise click.ClickException("Validation failed")
```

### 4. Schema Validation Pattern

```python
# src/fvc/tools/df/schema.py

import json
from jsonschema import validate, ValidationError
from typing import Optional

class SchemaValidator:
    def __init__(self):
        self.schema = self._load_schema()
    
    def _load_schema(self) -> dict:
        """Load schema from YAML file"""
        with open("src/fvc/tools/df/schema.yaml", "r") as f:
            return yaml.safe_load(f)
    
    def validate_file(self, file_path: str, verbose: bool = False) -> bool:
        """Validate .fvc file against schema"""
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
    
    def _validate_metadata(self, metadata: dict) -> None:
        """Validate METADATA record"""
        validate(instance=metadata, schema=self.schema["METADATA"])
    
    def _validate_record(self, record: dict, expected_content: str, line_num: int) -> None:
        """Validate data record"""
        # Check content type
        if record.get("content") and record["content"] != expected_content:
            raise ValidationError(
                f"Content mismatch at line {line_num}: "
                f"expected {expected_content}, got {record['content']}"
            )
        
        # Validate against appropriate schema
        content_type = expected_content
        if content_type in self.schema:
            validate(instance=record, schema=self.schema[content_type])
```

## Performance Best Practices

### 1. Use Polars for Data Processing

```python
# ✅ Good: Use Polars for large datasets
import polars as pl

df = pl.read_csv("large_file.csv")
result = df.filter(pl.col("alt") > 100.0).collect()

# ✅ Good: Use lazy evaluation
lazy_df = df.lazy()
result = lazy_df.filter(...).collect()

# ❌ Bad: Use Pandas for large datasets
import pandas as pd
df = pd.read_csv("large_file.csv")  # Slower and more memory
```

### 2. Streaming Processing

```python
# ✅ Good: Stream large files
with open("large_file.jsonl", "r") as f:
    for line in f:
        record = json.loads(line)
        process_record(record)

# ✅ Good: Use generators

def read_large_file(file_path: str):
    with open(file_path, "r") as f:
        for line in f:
            yield json.loads(line)

# Process records one at a time
for record in read_large_file("large_file.jsonl"):
    process_record(record)
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
```

### 4. Memory Management

```python
# ✅ Good: Use appropriate data types
pl.Int32()  # Instead of Int64 for timestamps
pl.Float32()  # Instead of Float64 for coordinates

# ✅ Good: Filter early
lazy_df.filter(pl.col("time") > start_time).collect()

# ✅ Good: Process in chunks
chunk_size = 10000
for chunk in df.iter_slices(chunk_size):
    process_chunk(chunk)

# ❌ Bad: Keep all data in memory
df = pl.read_csv("huge_file.csv")  # Loads entire file
result = df.filter(...).collect()
```

### 5. Caching

```python
# ✅ Good: Cache expensive operations
import functools

@functools.lru_cache(maxsize=100)
def get_geoid_undulation(lat: float, lon: float) -> float:
    """Cache geoid undulation calculations"""
    return calculate_undulation(lat, lon)

# ✅ Good: Cache DataFrame operations
df = pl.DataFrame(...)
cached = df.lazy().filter(...).collect()
```

## Testing Best Practices

### 1. Test Structure

```python
tests/
├── conftest.py               # Test fixtures
├── test_nmea_xformat.py      # NMEA format tests
├── test_ulog_xformat.py       # ULog format tests
├── test_conversion.py         # Conversion tests
├── test_validation.py         # Validation tests
├── test_cli.py                # CLI tests
├── test_polars_integration.py # Polars integration tests
└── test_performance.py        # Performance tests
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
```

### 3. Writing Tests

```python
# tests/test_nmea_xformat.py

import pytest
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_nmea_conversion(temp_dir, sample_nmea):
    """Test NMEA to .fvc conversion"""
    # Create test file
    input_file = temp_dir / "test.nmea"
    input_file.write_text(sample_nmea)
    
    # Convert
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    result = converter.convert(str(input_file), str(output_file))
    
    # Assert
    assert result is True
    assert output_file.exists()
    
    # Check output
    lines = output_file.read_text().strip().split("\n")
    assert len(lines) == 3  # METADATA + 2 records
    
    # Check METADATA
    metadata = eval(lines[0])
    assert metadata["content"] == "flightlog"
    assert metadata["source"] == "nmea"
    assert metadata["origin"] == str(input_file)

def test_nmea_empty_file(temp_dir):
    """Test handling of empty NMEA file"""
    input_file = temp_dir / "empty.nmea"
    input_file.write_text("")
    
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    
    with pytest.raises(Exception):
        converter.convert(str(input_file), str(output_file))

def test_nmea_invalid_sentence(temp_dir):
    """Test handling of invalid NMEA sentence"""
    invalid_data = "INVALID SENTENCE\n$GNGGA,..."
    input_file = temp_dir / "invalid.nmea"
    input_file.write_text(invalid_data)
    
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    result = converter.convert(str(input_file), str(output_file))
    
    # Should skip invalid sentence and continue
    assert result is True
```

### 4. Test Coverage

```python
# Run tests with coverage
pytest --cov=src/fvc --cov-report=term-missing

# Check coverage for specific module
pytest --cov=src/fvc/tools/df/core tests/test_conversion.py

# Generate HTML report
pytest --cov=src/fvc --cov-report=html
open htmlcov/index.html
```

**Aim for**:
- >80% overall coverage
- 100% coverage for critical paths
- Tests for edge cases
- Tests for error handling
- Integration tests

### 5. Property-Based Testing

```python
# tests/test_properties.py

import pytest
import hypothesis.strategies as st
from hypothesis import given
from fvc.tools.df.schema import SchemaValidator

@given(st.lists(st.floats(min_value=-90, max_value=90)))
def test_latitude_range(latitudes):
    """Test that latitude values are in valid range"""
    for lat in latitudes:
        assert -90 <= lat <= 90

@given(st.integers(min_value=0, max_value=2000000000))
def test_unix_timestamp(timestamp):
    """Test that Unix timestamps are reasonable"""
    # 2038 problem check
    assert timestamp < 2**31
```

## Documentation Best Practices

### 1. Docstrings

Use **Google style docstrings**:

```python
from typing import Optional

def convert(
    input_path: str,
    output_path: str,
    verbose: bool = False
) -> bool:
    """Convert external format to Flyvercity Data Format (.fvc)
    
    Args:
        input_path: Path to input file
        output_path: Path to output .fvc file
        verbose: Enable verbose output
        
    Returns:
        bool: True if conversion succeeded, False otherwise
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input format is invalid
        
    Examples:
        >>> converter = NMEAConverter()
        >>> converter.convert("flight.nmea", "flight.fvc")
        True
        
    Notes:
        - Validates output against schema
        - Preserves original data quality
        - Handles large files efficiently
    """
    ...
```

### 2. Type Hints in Documentation

```python
# In documentation:
# - `input_path` (str): Path to input file
# - `output_path` (str): Path to output .fvc file
# - `verbose` (bool): Enable verbose output
# - Returns: True if successful, False otherwise

# In code:
def convert(input_path: str, output_path: str, verbose: bool = False) -> bool:
    ...
```

### 3. Update Documentation with Code

**When you change code**:

1. Update function docstrings
2. Update module-level documentation
3. Update architecture diagrams if needed
4. Update workflow guides
5. Update related documentation pages

**Example**:

```python
# Before (old behavior):
def convert(input_path, output_path):
    """Convert file"""
    ...

# After (new behavior with Polars):
def convert(input_path: str, output_path: str, use_polars: bool = True) -> bool:
    """Convert external format to .fvc format
    
    Args:
        input_path: Path to input file
        output_path: Path to output .fvc file
        use_polars: Use Polars for optimization (default: True)
        
    Returns:
        bool: True if conversion succeeded
    """
    ...
```

Then update related documentation:
- [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md)
- [/openwiki/integrations/polars.md](/openwiki/integrations/polars.md)
- [/openwiki/workflows/conversion.md](/openwiki/workflows/conversion.md)

## Debugging and Profiling

### 1. Debugging Techniques

```python
# ✅ Good: Use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Processing record: %s", record)

# ✅ Good: Use pdb
import pdb; pdb.set_trace()

# ✅ Good: Use IDE debugger
# Set breakpoints in VS Code/PyCharm

# ✅ Good: Print intermediate values
print(f"DEBUG: df shape = {df.shape}")
print(f"DEBUG: records = {len(df)}")
```

### 2. Profiling Performance

```python
# ✅ Good: Use cProfile
import cProfile

pr = cProfile.Profile()
pr.enable()

# Your code here
convert("input.nmea", "output.fvc")

pr.disable()
pr.print_stats(sort="cumtime")

# ✅ Good: Use timeit for microbenchmarks
import timeit

time = timeit.timeit(
    "convert('input.nmea', 'output.fvc')",
    setup="from fvc.tools.df.xformats.nmea import NMEAConverter; converter = NMEAConverter()",
    number=10
)
print(f"Average time: {time / 10:.4f}s")

# ✅ Good: Use memory_profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Your code here
    ...
```

### 3. Common Debugging Scenarios

**Issue**: Conversion fails silently

```python
# Add debug logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add try-except with logging
try:
    converter.convert(input_path, output_path)
except Exception as e:
    logger.error("Conversion failed: %s", e, exc_info=True)
    raise
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
# - File I/O
# - Data processing
# - Memory usage
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

## Security Best Practices

### 1. Input Validation

```python
# ✅ Good: Validate file paths
import os

def safe_path(base_dir: str, relative_path: str) -> str:
    """Ensure path is within base directory"""
    full_path = os.path.abspath(os.path.join(base_dir, relative_path))
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Path traversal detected")
    return full_path

# ✅ Good: Validate file extensions
def allowed_extension(filename: str) -> bool:
    return filename.lower().endswith((".nmea", ".ulg", ".json", ".fvc"))

# ✅ Good: Sanitize inputs
import re

def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    return re.sub(r'[\\/:*?"<>|]', '_', filename)
```

### 2. Error Messages

```python
# ✅ Good: Generic error messages
raise ValueError("Invalid input format")

# ❌ Bad: Reveal system details
raise ValueError(f"File {file_path} not found on system /home/user/data")

# ✅ Good: Log errors, return user-friendly messages
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
~/.aws/credentials

# ✅ Good: Use IAM roles (for EC2, ECS)
# No credentials needed - use instance role

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
```

## Continuous Integration

### 1. GitHub Actions Workflow

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
```

## Release Process

### 1. Versioning

fvctools uses **semantic versioning**:

```
MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: Backward-compatible features
- PATCH: Backward-compatible bug fixes
```

**Examples**:
- `2026.5.12` - Version from pyproject.toml
- `1.0.0` - First stable release
- `1.1.0` - New features
- `1.0.1` - Bug fix

### 2. Changelog

Maintain a `CHANGELOG.md` or `CHANGELOG.rst`:

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

## [1.0.0] - 2026-01-01

### Added
- Initial release
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
```

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Architecture Overview](/openwiki/architecture/overview.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Setup Guide](/openwiki/operations/setup.md)
- [Testing Guide](/openwiki/testing/overview.md)
- [Integration Guides](/openwiki/integrations/index.md)

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

## Best Practices Summary

✅ **Write type hints** for all functions
✅ **Use pre-commit hooks** before committing
✅ **Write tests** for new functionality
✅ **Update documentation** with code changes
✅ **Follow PEP 8** with Ruff's stricter rules
✅ **Use logging** for debugging and monitoring
✅ **Validate inputs** early
✅ **Handle errors gracefully**
✅ **Profile performance** before optimizing
✅ **Keep commits small and focused**
✅ **Write good commit messages**
✅ **Review your own PRs** before requesting review
✅ **Update CHANGELOG** for releases

## Next Steps

- **Set up development environment**: [/openwiki/operations/setup.md](/openwiki/operations/setup.md)
- **Learn architecture**: [/openwiki/architecture/overview.md](/openwiki/architecture/overview.md)
- **Explore CLI tools**: [/openwiki/architecture/tools.md](/openwiki/architecture/tools.md)
- **Write your first contribution**: Start with a bug fix or small feature
