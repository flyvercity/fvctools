---
type: Testing Guide
title: Testing Overview and Best Practices

description: Overview of testing strategies, tools, and best practices for fvctools
resource: /tests

tags: [testing, pytest, quality, best-practices, coverage]
---

# Testing Overview and Best Practices

This guide provides an overview of testing strategies, tools, and best practices for **fvctools**.

## Overview

Testing is critical for ensuring the reliability, correctness, and maintainability of fvctools. This guide covers:

- **Testing strategies** and methodologies
- **Test organization** and structure
- **Testing tools** and frameworks
- **Best practices** for writing maintainable tests
- **Performance testing** and optimization
- **Integration testing** with external systems
- **Test automation** and CI/CD

## Testing Philosophy

### 1. Test Pyramid

fvctools follows the **test pyramid** principle:

```
High Level: Integration & E2E Tests (10-20%)
   ↓
Medium Level: Service & Component Tests (20-30%)
   ↓
Low Level: Unit Tests (60-70%)
```

**Unit Tests**: Test individual functions and methods
**Component Tests**: Test modules and classes
**Integration Tests**: Test interactions between components
**E2E Tests**: Test complete workflows

### 2. Test-Driven Development (TDD)

When adding new features or fixing bugs:

1. ✅ Write tests first (or alongside code)
2. ✅ Implement functionality
3. ✅ Verify tests pass
4. ✅ Refactor
5. ✅ Add more tests if needed

### 3. Test Quality

**Good tests are**:

- ✅ **Fast**: Run in milliseconds, not minutes
- ✅ **Isolated**: Don't depend on external state
- ✅ **Deterministic**: Same input → same output
- ✅ **Readable**: Clear what's being tested
- ✅ **Maintainable**: Easy to update when code changes
- ✅ **Comprehensive**: Cover edge cases

**Bad tests are**:

- ❌ Slow (integration tests that run every time)
- ❌ Flaky (sometimes pass, sometimes fail)
- ❌ Brittle (break on minor code changes)
- ❌ Duplicative (test same thing multiple times)
- ❌ Untested (no assertions)

## Testing Tools

### 1. pytest - The Testing Framework

**Why pytest**:

- ✅ Simple and expressive syntax
- ✅ Rich plugin ecosystem
- ✅ Excellent fixture system
- ✅ Powerful assertion introspection
- ✅ Detailed failure information
- ✅ Parallel test execution

**Installation**:

```bash
# Already included in dev dependencies
uv pip install pytest
```

**Basic usage**:

```python
# test_example.py

def test_addition():
    """Test that addition works"""
    assert 1 + 1 == 2

def test_subtraction():
    """Test that subtraction works"""
    assert 3 - 1 == 2
```

**Run tests**:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_example.py

# Run specific test function
pytest tests/test_example.py::test_addition

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/fvc --cov-report=html

# Run in watch mode (if using pytest-watch)
ptw
```

### 2. pytest Plugins

**Installed plugins**:

| Plugin | Purpose |
|--------|---------|
| `pytest-cov` | Coverage reporting |
| `pytest-xdist` | Parallel test execution |
| `pytest-timeout` | Timeout for slow tests |
| `pytest-mock` | Mocking utilities |
| `hypothesis` | Property-based testing |

**Install additional plugins**:

```bash
uv pip install pytest-asyncio pytest-benchmark
```

### 3. Coverage.py - Code Coverage

**Why coverage**:

- ✅ Measure test coverage
- ✅ Identify untested code
- ✅ Set coverage targets
- ✅ Generate reports

**Installation**:

```bash
uv pip install pytest-cov
```

**Usage**:

```bash
# Run tests with coverage
pytest --cov=src/fvc --cov-report=term-missing

# Generate HTML report
pytest --cov=src/fvc --cov-report=html
open htmlcov/index.html

# Set minimum coverage (in pytest.ini)
[tool:pytest]
addopts = --cov=src/fvc --cov-report=term-missing --cov-fail-under=80
```

### 4. Hypothesis - Property-Based Testing

**Why Hypothesis**:

- ✅ Generate test cases automatically
- ✅ Test edge cases you might miss
- ✅ Shrink failing test cases
- ✅ Improve test coverage

**Installation**:

```bash
uv pip install hypothesis
```

**Usage**:

```python
# tests/test_properties.py

import pytest
import hypothesis.strategies as st
from hypothesis import given

@given(st.integers(), st.integers())
def test_add_commutative(a, b):
    """Addition is commutative: a + b == b + a"""
    assert a + b == b + a

@given(st.lists(st.floats(min_value=-90, max_value=90)))
def test_latitude_range(latitudes):
    """Latitude values must be between -90 and 90"""
    for lat in latitudes:
        assert -90 <= lat <= 90
```

### 5. pytest-mock - Mocking Utilities

**Why mocking**:

- ✅ Test code without external dependencies
- ✅ Isolate components for testing
- ✅ Simulate error conditions
- ✅ Speed up tests

**Installation**:

```bash
uv pip install pytest-mock
```

**Usage**:

```python
# tests/test_mocking.py

def test_mock_external_api(mocker):
    """Test code that calls external API"""
    # Mock the API call
    mock_api = mocker.patch('module.external_api.call')
    mock_api.return_value = {'result': 'success'}
    
    # Test your code
    result = my_function_that_calls_api()
    
    # Assert API was called
    mock_api.assert_called_once()
    assert result == {'result': 'success'}
```

### 6. pytest-xdist - Parallel Testing

**Why parallel testing**:

- ✅ Faster test execution
- ✅ Better resource utilization
- ✅ CI/CD optimization

**Installation**:

```bash
uv pip install pytest-xdist
```

**Usage**:

```bash
# Run tests in parallel
pytest -n auto  # Use all available CPUs

# Run with specific number of workers
pytest -n 4

# Run with distribution
pytest -n auto --dist=loadfile
```

## Test Organization

### 1. Directory Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Test fixtures and plugins
├── test_*.py                # Test files
│   ├── test_nmea_xformat.py
│   ├── test_ulog_xformat.py
│   ├── test_conversion.py
│   ├── test_validation.py
│   ├── test_cli.py
│   └── test_polars_integration.py
├── fixtures/                # Test data fixtures
│   ├── nmea_samples.py
│   ├── flight_records.py
│   └── schema_samples.py
└── utils.py                 # Test utilities
```

### 2. Test File Naming

**Convention**: `test_<module>_<feature>.py`

**Examples**:
- `test_nmea_xformat.py` - NMEA format converter tests
- `test_ulog_xformat.py` - ULog format converter tests
- `test_conversion.py` - General conversion tests
- `test_validation.py` - Validation tests
- `test_cli.py` - CLI tests
- `test_polars_integration.py` - Polars integration tests

### 3. Test Function Naming

**Convention**: `test_<function>_<scenario>`

**Examples**:
- `test_convert_valid_nmea_file()` - Test valid NMEA conversion
- `test_convert_empty_file()` - Test empty file handling
- `test_validate_correct_schema()` - Test schema validation
- `test_cli_help_command()` - Test CLI help command

### 4. Test Fixtures (conftest.py)

**Common fixtures**:

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
def valid_fvc_file(temp_dir):
    """Create a valid .fvc file for testing"""
    file_path = temp_dir / "valid.fvc"
    file_path.write_text(sample_flight())
    return file_path
```

### 5. Test Utilities

```python
# tests/utils.py

import json
from pathlib import Path

def read_fvc_file(file_path: Path) -> list:
    """Read .fvc file and return records"""
    with open(file_path, "r") as f:
        return [json.loads(line) for line in f]

def write_fvc_file(file_path: Path, records: list) -> None:
    """Write records to .fvc file"""
    with open(file_path, "w") as f:
        for record in records:
            f.write(f"{json.dumps(record)}\n")

def assert_fvc_valid(file_path: Path) -> None:
    """Assert that .fvc file is valid"""
    from fvc.tools.df.schema import SchemaValidator
    validator = SchemaValidator()
    assert validator.validate_file(str(file_path), verbose=True)
```

## Writing Good Tests

### 1. Unit Tests

**Test individual functions and methods**:

```python
# tests/test_utils.py

from fvc.tools.df.utils import parse_timestamp

def test_parse_timestamp_valid():
    """Test parsing valid Unix timestamp"""
    result = parse_timestamp(1756033206882)
    assert result == {"unix": 1756033206882, "iso": "2025-04-25T10:20:06.882Z"}

def test_parse_timestamp_invalid():
    """Test handling of invalid timestamp"""
    with pytest.raises(ValueError):
        parse_timestamp(-1)
```

**Best practices**:

- ✅ Test one thing per test
- ✅ Use descriptive names
- ✅ Include edge cases
- ✅ Test error conditions
- ✅ Keep tests simple

### 2. Component Tests

**Test modules and classes**:

```python
# tests/test_metadata.py

from fvc.tools.df.metadata import Metadata

def test_metadata_create():
    """Test creating METADATA record"""
    metadata = Metadata(
        content="flightlog",
        source="nmea",
        origin="test.log"
    )
    assert metadata.content == "flightlog"
    assert metadata.source == "nmea"
    assert metadata.origin == "test.log"

def test_metadata_to_dict():
    """Test converting METADATA to dict"""
    metadata = Metadata(
        content="flightlog",
        source="nmea",
        origin="test.log"
    )
    result = metadata.to_dict()
    assert result == {
        "content": "flightlog",
        "source": "nmea",
        "origin": "test.log"
    }
```

### 3. Integration Tests

**Test interactions between components**:

```python
# tests/test_conversion_pipeline.py

from fvc.tools.df.core import ConversionEngine

def test_full_conversion_pipeline(temp_dir, sample_nmea):
    """Test complete conversion pipeline"""
    # Create test file
    input_file = temp_dir / "input.nmea"
    input_file.write_text(sample_nmea)
    
    # Convert
    engine = ConversionEngine()
    output_file = temp_dir / "output.fvc"
    result = engine.convert(
        str(input_file), 
        "nmea", 
        str(output_file)
    )
    
    # Assert
    assert result is True
    assert output_file.exists()
    
    # Validate
    from fvc.tools.df.schema import SchemaValidator
    validator = SchemaValidator()
    assert validator.validate_file(str(output_file))
```

### 4. End-to-End Tests

**Test complete workflows**:

```python
# tests/test_e2e_workflow.py

import subprocess
import tempfile
from pathlib import Path

def test_full_workflow():
    """Test complete workflow from CLI"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test input
        input_file = Path(tmpdir) / "input.nmea"
        input_file.write_text("$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46")
        
        # Run CLI command
        result = subprocess.run(
            ["uv", "run", "fvc", "df", "--in", str(input_file), "convert", "nmea", "output.fvc"],
            capture_output=True,
            text=True
        )
        
        # Assert
        assert result.returncode == 0
        assert Path(tmpdir / "output.fvc").exists()
```

## Testing Strategies

### 1. Test Coverage Targets

**Aim for**:

- ✅ **80%+ overall coverage** (minimum)
- ✅ **100% coverage for critical paths**
- ✅ **Edge cases covered**
- ✅ **Error handling tested**

**Check coverage**:

```bash
# Run tests with coverage
pytest --cov=src/fvc --cov-report=term-missing

# Set minimum coverage in pytest.ini
[tool:pytest]
addopts = --cov=src/fvc --cov-report=term-missing --cov-fail-under=80
```

### 2. Edge Case Testing

**Test boundary conditions**:

```python
# tests/test_edge_cases.py

import pytest
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_empty_file(temp_dir):
    """Test handling of empty input file"""
    input_file = temp_dir / "empty.nmea"
    input_file.write_text("")
    
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    
    with pytest.raises(Exception):
        converter.convert(str(input_file), str(output_file))

def test_file_with_only_comments(temp_dir):
    """Test handling of file with only comments"""
    input_file = temp_dir / "comments.nmea"
    input_file.write_text("# This is a comment\n$GNGGA,...")
    
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    result = converter.convert(str(input_file), str(output_file))
    
    # Should skip comments and process valid sentences
    assert result is True

def test_large_file(temp_dir):
    """Test handling of large file"""
    # Create large file
    large_data = "$GNGGA,...\n" * 10000
    input_file = temp_dir / "large.nmea"
    input_file.write_text(large_data)
    
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    result = converter.convert(str(input_file), str(output_file))
    
    assert result is True
    assert output_file.exists()
```

### 3. Error Handling Testing

**Test error conditions**:

```python
# tests/test_error_handling.py

import pytest
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_file_not_found():
    """Test handling of non-existent file"""
    converter = NMEAConverter()
    
    with pytest.raises(FileNotFoundError):
        converter.convert("nonexistent.nmea", "output.fvc")

def test_invalid_format():
    """Test handling of invalid format"""
    converter = NMEAConverter()
    
    with pytest.raises(ValueError):
        converter.convert("invalid.txt", "output.fvc")

def test_permission_denied(temp_dir):
    """Test handling of permission denied"""
    input_file = temp_dir / "no_permission.nmea"
    input_file.write_text("$GNGGA,...")
    input_file.chmod(0o000)  # No permissions
    
    converter = NMEAConverter()
    output_file = temp_dir / "output.fvc"
    
    with pytest.raises(PermissionError):
        converter.convert(str(input_file), str(output_file))
```

### 4. Property-Based Testing

**Use Hypothesis for automatic test case generation**:

```python
# tests/test_properties.py

import pytest
import hypothesis.strategies as st
from hypothesis import given
from fvc.tools.df.schema import SchemaValidator

def test_schema_validation_properties():
    """Test schema validation properties"""
    validator = SchemaValidator()
    
    # Test that valid data passes validation
    @given(st.dictionaries(
        st.text(min_size=1, max_size=50),
        st.one_of(
            st.text(),
            st.integers(),
            st.floats(),
            st.booleans(),
            st.none()
        )
    ))
    def test_valid_data_passes(data):
        # This would need actual schema constraints
        pass

@given(st.lists(st.floats(min_value=-90, max_value=90)))
def test_latitude_range(latitudes):
    """Latitude values must be between -90 and 90"""
    for lat in latitudes:
        assert -90 <= lat <= 90

@given(st.integers(min_value=0, max_value=2000000000))
def test_unix_timestamp(timestamp):
    """Unix timestamps should be reasonable"""
    # 2038 problem check
    assert timestamp < 2**31
```

### 5. Performance Testing

**Test performance characteristics**:

```python
# tests/test_performance.py

import time
import pytest
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_conversion_performance(temp_dir):
    """Test conversion performance"""
    # Create test data
    data = "$GNGGA,...\n" * 1000
    input_file = temp_dir / "perf_test.nmea"
    input_file.write_text(data)
    
    converter = NMEAConverter()
    output_file = temp_dir / "perf_output.fvc"
    
    # Time the conversion
    start = time.time()
    result = converter.convert(str(input_file), str(output_file))
    duration = time.time() - start
    
    # Assert performance
    assert result is True
    assert duration < 1.0  # Should complete in under 1 second
    
    # Print performance metrics
    print(f"\nPerformance: {duration:.4f}s for 1000 records")
    print(f"Records per second: {1000 / duration:.2f}")

@pytest.mark.benchmark
def test_large_file_performance(benchmark):
    """Benchmark large file conversion"""
    # This would use pytest-benchmark
    pass
```

## Test Automation

### 1. GitHub Actions CI/CD

**Example workflow**:

```yaml
# .github/workflows/ci.yml

name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
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
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

### 2. Test Matrix

**Test multiple Python versions**:

```yaml
strategy:
  matrix:
    python-version: ["3.12", "3.13"]
```

**Test multiple platforms**:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### 3. Test Reporting

**Generate test reports**:

```yaml
- name: Generate test report
  run: |
    pytest --junitxml=test-results.xml
  
- name: Upload test results
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.xml
```

### 4. Code Coverage

**Upload coverage to Codecov**:

```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

## Test Maintenance

### 1. Test Refactoring

**When code changes, update tests**:

```python
# Old test (before refactoring)
def test_old_api():
    from fvc.tools.df.old_module import old_function
    result = old_function("input")
    assert result == "expected"

# New test (after refactoring)
def test_new_api():
    from fvc.tools.df.new_module import new_function
    result = new_function("input")
    assert result == "expected"
```

### 2. Deprecation Testing

**Test deprecated functionality**:

```python
# tests/test_deprecations.py

import pytest
import warnings
from fvc.tools.df.old_module import deprecated_function

def test_deprecated_function():
    """Test that deprecated function still works"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = deprecated_function("input")
        
        # Check deprecation warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()
        
        # Check function still works
        assert result == "expected"
```

### 3. Test Documentation

**Keep test documentation up to date**:

```python

def test_example():
    """
    Test that demonstrates usage of the API.
    
    This test shows how to use the convert function:
    
    Example:
        >>> from fvc.tools.df.core import ConversionEngine
        >>> engine = ConversionEngine()
        >>> engine.convert("input.nmea", "nmea", "output.fvc")
        True
    """
    ...
```

## Performance Testing

### 1. Benchmarking

**Use pytest-benchmark**:

```python
# tests/test_benchmarks.py

import pytest
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_conversion_benchmark(benchmark):
    """Benchmark NMEA conversion"""
    converter = NMEAConverter()
    
    def convert():
        converter.convert("test.nmea", "output.fvc")
    
    result = benchmark(convert)
    assert result is True
```

**Install pytest-benchmark**:

```bash
uv pip install pytest-benchmark
```

### 2. Performance Regression Testing

**Detect performance regressions**:

```python
# tests/test_performance_regression.py

import pytest
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_no_performance_regression(benchmark):
    """Ensure conversion doesn't get slower"""
    converter = NMEAConverter()
    
    # Baseline: 0.5 seconds for 1000 records
    result = benchmark.pedantic(
        converter.convert,
        args=("test.nmea", "output.fvc"),
        rounds=10,
        iterations=100
    )
    
    assert result is True
    assert benchmark.stats.mean < 0.5
```

### 3. Memory Profiling

**Profile memory usage**:

```python
# tests/test_memory.py

from memory_profiler import profile
from fvc.tools.df.xformats.nmea import NMEAConverter

@profile
def test_memory_usage():
    """Profile memory usage of conversion"""
    converter = NMEAConverter()
    converter.convert("large.nmea", "output.fvc")
```

**Install memory_profiler**:

```bash
uv pip install memory-profiler
```

## Integration Testing

### 1. External System Testing

**Test with real external systems**:

```python
# tests/test_external_systems.py

import pytest
from fvc.tools.df.xformats.safirmqtt import SAFIRMQTTConverter

def test_safir_mqtt_integration():
    """Test SAFIR MQTT integration (if available)"""
    try:
        converter = SAFIRMQTTConverter()
        # Test with real MQTT broker
        result = converter.convert("mqtt://broker:1883/topic", "output.fvc")
        assert result is True
    except Exception as e:
        pytest.skip(f"MQTT integration not available: {e}")
```

### 2. API Testing

**Test API integrations**:

```python
# tests/test_api_integrations.py

import pytest
import requests
from unittest.mock import patch

def test_api_integration():
    """Test API integration with mock"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"result": "success"}
        
        response = requests.get("https://api.example.com/data")
        assert response.status_code == 200
        assert response.json() == {"result": "success"}
```

### 3. Database Testing

**Test database integrations**:

```python
# tests/test_database.py

import pytest
from fvc.tools.db import Database

@pytest.fixture
def db():
    """Create test database"""
    db = Database(":memory:")  # SQLite in-memory database
    db.create_tables()
    return db

def test_database_operations(db):
    """Test database operations"""
    # Test insert
    db.insert_record({"time": 123, "lat": 52.3, "lon": 4.9})
    
    # Test query
    result = db.get_records()
    assert len(result) == 1
    assert result[0]["lat"] == 52.3
```

## Test Best Practices

### 1. Keep Tests Fast

**Fast tests run more often**:

```python
# ✅ Good: Fast test

def test_simple_function():
    result = simple_function(1, 2)
    assert result == 3

# ❌ Bad: Slow test (integration test that runs every time)

def test_external_api():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200
```

**Solutions**:
- ✅ Use mocks for external dependencies
- ✅ Test in-memory instead of on disk
- ✅ Use efficient algorithms
- ✅ Avoid sleep() in tests

### 2. Keep Tests Isolated

**Tests should not depend on each other**:

```python
# ✅ Good: Each test creates its own state

def test_first_feature():
    state = create_state()
    result = feature1(state)
    assert result == expected

def test_second_feature():
    state = create_state()  # Different state
    result = feature2(state)
    assert result == expected

# ❌ Bad: Tests share state
state = None

def test_first():
    global state
    state = create_state()
    ...

def test_second():
    # Depends on first test setting state
    result = feature2(state)
    ...
```

### 3. Keep Tests Deterministic

**Same input → same output**:

```python
# ✅ Good: Deterministic
def test_deterministic():
    result = function(1, 2)
    assert result == 3

# ❌ Bad: Non-deterministic (depends on random)
def test_nondeterministic():
    result = function(random.randint(1, 10))
    # Can't predict result
```

**Solutions**:
- ✅ Don't use random() in tests
- ✅ Don't depend on current time
- ✅ Don't depend on external state
- ✅ Use fixed seed for random tests

### 4. Keep Tests Readable

**Clear what's being tested**:

```python
# ✅ Good: Clear and readable

def test_addition():
    """Test that addition works correctly"""
    result = add(2, 3)
    assert result == 5

# ❌ Bad: Unclear what's being tested

def test_math():
    assert add(2, 3) == 5
```

**Best practices**:
- ✅ Use descriptive function names
- ✅ Include docstrings explaining the test
- ✅ Keep tests focused (one assertion per test)
- ✅ Use clear variable names

### 5. Keep Tests Maintainable

**Easy to update when code changes**:

```python
# ✅ Good: Tests are easy to update

def test_conversion():
    """Test that converter works"""
    converter = NMEAConverter()
    result = converter.convert("input.nmea", "output.fvc")
    assert result is True

# ❌ Bad: Brittle test that breaks on minor changes

def test_exact_output():
    """Test exact output format"""
    result = format_output({"a": 1})
    assert result == '{"a": 1, "b": null}'  # Breaks if format changes
```

**Solutions**:
- ✅ Test behavior, not implementation
- ✅ Test public API, not internals
- ✅ Use flexible assertions
- ✅ Avoid testing exact string matches

## Test Documentation

### 1. Test Documentation

**Document what each test does**:

```python

def test_convert_valid_nmea_file():
    """
    Test that valid NMEA files are converted correctly.
    
    This test verifies:
    - METADATA is written correctly
    - Data records are parsed
    - Output file is valid .fvc format
    - All required fields are present
    
    Related: /openwiki/workflows/conversion.md
    """
    ...
```

### 2. Test Coverage Reports

**Generate and review coverage reports**:

```bash
# Run tests with coverage
pytest --cov=src/fvc --cov-report=html

# Open HTML report
open htmlcov/index.html

# Check coverage for specific module
pytest --cov=src/fvc/tools/df/core tests/test_conversion.py
```

### 3. Test Reports in CI

**Include test reports in CI output**:

```yaml
- name: Run tests
  run: pytest --junitxml=test-results.xml --cov=src/fvc --cov-report=xml

- name: Upload test results
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.xml
```

## Common Testing Patterns

### 1. Arrange-Act-Assert Pattern

**Standard test structure**:

```python

def test_example():
    # Arrange: Set up test data and state
    input_data = {"time": 123, "lat": 52.3, "lon": 4.9}
    
    # Act: Call the function/method under test
    result = process_data(input_data)
    
    # Assert: Verify the result
    assert result["alt"] == 100.5
```

### 2. Parameterized Testing

**Test multiple inputs with pytest**:

```python
# tests/test_parameterized.py

import pytest

@pytest.mark.parametrize("input,expected", [
    ("1", 1),
    ("2", 2),
    ("10", 10),
])
def test_parse_integer(input, expected):
    """Test parsing integers"""
    result = int(input)
    assert result == expected
```

### 3. Mocking External Dependencies

**Isolate from external systems**:

```python
# tests/test_with_mocks.py

from unittest.mock import patch
from fvc.tools.df.xformats.nmea import NMEAConverter

def test_with_mocked_api():
    """Test with mocked external API"""
    with patch('module.external_api.call') as mock_api:
        mock_api.return_value = {"result": "success"}
        
        converter = NMEAConverter()
        result = converter.convert("input.nmea", "output.fvc")
        
        assert result is True
        mock_api.assert_called_once()
```

### 4. Testing Exceptions

**Test that exceptions are raised**:

```python

def test_raises_exception():
    """Test that function raises exception for invalid input"""
    with pytest.raises(ValueError):
        function_that_should_fail("invalid_input")
```

### 5. Testing Side Effects

**Test that functions have expected side effects**:

```python

def test_side_effects():
    """Test that function modifies state correctly"""
    state = {"count": 0}
    
    def increment():
        state["count"] += 1
    
    increment()
    assert state["count"] == 1
```

## Debugging Failing Tests

### 1. Understanding Test Failures

**Common failure types**:

- ✅ **AssertionError**: Test condition not met
- ✅ **ValueError**: Invalid input or operation
- ✅ **TypeError**: Wrong type passed
- ✅ **FileNotFoundError**: File missing
- ✅ **PermissionError**: Permission denied
- ✅ **TimeoutError**: Test took too long

### 2. Debugging Techniques

**Use pytest's debugging features**:

```bash
# Run specific test with verbose output
pytest tests/test_example.py::test_function -vv

# Drop into pdb on failure
pytest --pdb

# Run test and enter pdb on failure
pytest --pdb-failures

# Print variables in test
pytest --showlocals
```

**In code**:

```python
# Use pdb
import pdb; pdb.set_trace()

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Variable value: %s", variable)
```

### 3. Common Test Issues

#### Issue: Test is flaky

**Symptoms**: Test sometimes passes, sometimes fails

**Causes**:
- ❌ Random() usage
- ❌ External dependencies
- ❌ Race conditions
- ❌ Time-dependent logic
- ❌ Shared state

**Solutions**:

```python
# ✅ Good: Use fixed seed for random
import random
random.seed(42)

# ✅ Good: Mock external dependencies
from unittest.mock import patch

with patch('module.external_api.call'):
    # Test code
    ...

# ✅ Good: Avoid shared state
# Create fresh state for each test
```

#### Issue: Test is slow

**Symptoms**: Test takes too long to run

**Causes**:
- ❌ Integration tests in unit test suite
- ❌ File I/O operations
- ❌ External API calls
- ❌ Large test data

**Solutions**:

```python
# ✅ Good: Use in-memory operations
# Instead of file I/O

# ✅ Good: Mock slow dependencies
from unittest.mock import patch

with patch('module.slow_function'):
    # Test code
    ...

# ✅ Good: Use smaller test data
# Generate test data programmatically
```

#### Issue: Test is brittle

**Symptoms**: Test breaks on minor code changes

**Causes**:
- ❌ Testing implementation details
- ❌ Exact string matching
- ❌ Overly specific assertions
- ❌ Testing private methods

**Solutions**:

```python
# ✅ Good: Test behavior, not implementation
# Test public API

# ✅ Good: Use flexible assertions
assert result > 0  # Instead of assert result == 5

# ✅ Good: Test public methods
# Instead of private methods
```

## Test Infrastructure

### 1. Test Fixtures

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
def sample_flight():
    """Sample flight data in .fvc format"""
    return '{"content": "flightlog", "source": "nmea", "origin": "test.log"}'
```

### 2. Test Data Management

**Organize test data**:

```
tests/
├── fixtures/
│   ├── nmea/
│   │   ├── basic.nmea
│   │   ├── edge_cases.nmea
│   │   └── large.nmea
│   ├── flightlogs/
│   │   ├── valid.fvc
│   │   └── invalid.fvc
│   └── schemas/
│       ├── flightlog.yaml
│       └── radarlog.yaml
```

### 3. Test Utilities

**Reusable test utilities**:

```python
# tests/utils.py

import json
from pathlib import Path

def read_fvc(file_path: Path) -> list:
    """Read .fvc file"""
    with open(file_path) as f:
        return [json.loads(line) for line in f]

def write_fvc(file_path: Path, records: list) -> None:
    """Write .fvc file"""
    with open(file_path, "w") as f:
        for record in records:
            f.write(f"{json.dumps(record)}\n")

def assert_valid_fvc(file_path: Path) -> None:
    """Assert .fvc file is valid"""
    from fvc.tools.df.schema import SchemaValidator
    validator = SchemaValidator()
    assert validator.validate_file(str(file_path))
```

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Development Setup](/openwiki/operations/setup.md)
- [Development Practices](/openwiki/operations/development.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Architecture Overview](/openwiki/architecture/overview.md)

## Quick Reference

| Task | Command/Tool |
|------|--------------|
| Run tests | `pytest` |
| Run specific test | `pytest tests/test_file.py::test_function` |
| Run with coverage | `pytest --cov=src/fvc` |
| Run in watch mode | `ptw` (if installed) |
| Generate HTML coverage | `pytest --cov=src/fvc --cov-report=html` |
| Check types | `mypy src/fvc` |
| Run pre-commit hooks | `pre-commit run --all-files` |
| Run benchmarks | `pytest --benchmark-only` |

## Best Practices Summary

✅ **Write tests first** (TDD approach)
✅ **Keep tests fast** (unit tests < 100ms)
✅ **Keep tests isolated** (no shared state)
✅ **Keep tests deterministic** (same input → same output)
✅ **Keep tests readable** (clear what's being tested)
✅ **Keep tests maintainable** (easy to update)
✅ **Test edge cases** (nulls, empty inputs, boundaries)
✅ **Test error conditions** (exceptions, invalid inputs)
✅ **Use mocks for external dependencies**
✅ **Aim for 80%+ coverage** (100% for critical paths)
✅ **Run tests in CI** (GitHub Actions)
✅ **Monitor test performance** (detect regressions)
✅ **Document tests** (what and why they test)
✅ **Refactor tests** when code changes
✅ **Use property-based testing** (Hypothesis)
✅ **Profile performance** (memory and CPU)
✅ **Test integration points** (external systems)
✅ **Keep test infrastructure clean** (fixtures, utilities)

## Next Steps

- **Set up CI/CD**: Configure GitHub Actions for automated testing
- **Add property-based tests**: Use Hypothesis for edge case testing
- **Profile test performance**: Identify and fix slow tests
- **Expand test coverage**: Aim for 80%+ overall coverage
- **Document test strategies**: Add to development guide
- **Set up code coverage tracking**: Use Codecov
