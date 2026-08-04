---
type: Guide
title: Quickstart Guide

description: Get started with fvctools - install, convert data, validate, and visualize flight logs
resource: /README.md

tags: [quickstart, tutorial, guide, fvctools, installation]
---

# Quickstart Guide

Welcome to **fvctools**! This guide will help you get started with the Flyvercity CLI Tools Suite.

## What is fvctools?

fvctools is a **modular Python-based CLI suite** designed for processing, converting, and validating geospatial aviation data. It serves as the backbone of Flyvercity's data pipeline, enabling seamless data integration and analysis across different platforms and formats.

## Key Features

✅ **Unified Data Format**: Convert multiple aviation formats to the Flyvercity Data Format (.fvc)
✅ **Schema Validation**: Strict validation ensures data quality
✅ **High Performance**: Optimized with Polars for fast processing
✅ **Modular Design**: Separate toolsets for different tasks
✅ **CLI-Centric**: Easy-to-use command-line interface
✅ **Extensible**: Add support for new formats easily

## Supported Formats

| Format | Description |
|--------|-------------|
| **NMEA** | Standard GPS protocol |
| **ULog** | PX4 flight controller logs |
| **SAFIR MQTT** | Telemetry streaming |
| **DatCon** | Flight recorder format |
| **SenHive** | Flight logging system |
| **AgentFly** | Simulator logs |
| **GeoJSON** | Geographic features |
| **KML** | Google Earth format |

## Installation

### Prerequisites

- ✅ **Python 3.12+**
- ✅ **uv** package manager (recommended)
- ✅ **Git** (for cloning repository)

### Install fvctools

#### Method 1: From Git Repository (Development)

```bash
# Clone repository
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Install in development mode (includes dev tools)
uv pip install -e ".[dev]"

# Verify installation
fvc --version
```

#### Method 2: From Git Repository (Production)

```bash
# Clone repository
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Install production dependencies only
uv pip install .

# Verify installation
fvc --version
```

#### Method 3: Using Installation Scripts

```bash
# Unix Shells (Linux, macOS, WSL)
source scripts/Login-ToCodeArtifact.sh
./scripts/Install-FvcTools.sh

# PowerShell (Windows)
."scripts\Login-ToCodeArtifact.ps1"
."scripts\Install-FvcTools.ps1"
```

### Verify Installation

```bash
# Check version
fvc --version

# Expected output:
# fvctools 2026.5.12

# Check help
fvc --help

# Expected output:
# Usage: fvc [OPTIONS] COMMAND [ARGS]...
#
# Flyvercity CLI Tools Suite
#
# Options:
# --version  Show version and exit
# --help     Show this message and exit.
# ...
```

## The Flyvercity Data Format (.fvc)

The `.fvc` format is the **unified data standard** used by all fvctools.

### Format Specification

- **Type**: JSON-Lines (`.jsonl`)
- **Structure**: One record per line
- **First line**: METADATA record
- **Subsequent lines**: Data records

### Example .fvc File

```json
{"content": "flightlog", "source": "nmea", "origin": "flight_data_20231201.log"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}}
{"time": {"unix": 1756033206883}, "pos": {"loc": {"lat": 52.3001, "lon": 4.9001, "alt": 100.8}}}
```

### METADATA Record

The METADATA record describes the file:

```json
{
  "content": "flightlog",
  "source": "nmea",
  "origin": "flight_data.log"
}
```

**Fields**:
- `content`: Type of data (`flightlog`, `radarlog`, `fusion.replay`, `capture.message`)
- `source`: Original format (`nmea`, `ulog`, `safirmqtt`, etc.)
- `origin`: Source file name or system name

## Basic Workflow

Here's a typical workflow with fvctools:

```
External Format → Convert to .fvc → Validate → Analyze → Visualize
```

### Step 1: Convert External Format to .fvc

```bash
# Convert NMEA file to .fvc
fvc df --in flight.nmea convert nmea flight.fvc

# Or using positional arguments
fvc df flight.nmea convert nmea flight.fvc
```

**Supported formats**:
- `nmea` - NMEA 0183 GPS protocol
- `ulog` - PX4 ULog format
- `safirmqtt` - SAFIR MQTT telemetry
- `datcon` - DatCon flight recorder format
- `senhive` - SenHive flight logging system
- `agentfly` - AgentFly simulator logs
- `geojson` - GeoJSON geographic features
- `kml` - KML Google Earth format

### Step 2: Validate the .fvc File

```bash
# Validate .fvc file
fvc df --in flight.fvc validate

# With verbose output (shows errors)
fvc df --in flight.fvc validate --verbose
```

**Validation checks**:
- ✅ METADATA is valid and first line
- ✅ Content type matches data records
- ✅ All required fields are present
- ✅ Field types are correct
- ✅ Values are within valid ranges

### Step 3: Analyze the Data

```bash
# Generate statistics
fvc tools flightlog stats flight.fvc

# Get geoid undulation
fvc calc undulation 52.3 4.9

# Get terrain elevation
fvc calc terrain 52.3 4.9 100.5
```

### Step 4: Visualize the Data

```bash
# Generate interactive HTML map
fvc render fl flight.fvc --output ./flight_map

# Open the visualization
open ./flight_map/index.html
```

**Output formats**:
- ✅ **HTML**: Interactive map with Leaflet.js
- ✅ **KML**: Google Earth format
- ✅ **JSON**: Raw data export

## Tutorial: Complete Workflow

Let's walk through a complete example using sample data.

### Step 1: Get Sample Data

```bash
# Create sample NMEA file
cat > sample.nmea << 'EOF'
$GNGGA,123456.78,5234.1234,N,00450.1234,E,1,12,1.2,100.5,M,48.2,M,,*46
$GNRMC,123456.78,A,5234.1234,N,00450.1234,E,6.1,45.0,010123,0.0,E,A*1C
$GNGGA,123457.78,5234.1235,N,00450.1235,E,1,12,1.2,101.0,M,48.2,M,,*47
$GNRMC,123457.78,A,5234.1235,N,00450.1235,E,6.2,45.1,010123,0.0,E,A*1D
EOF

# Check file
ls -la sample.nmea
cat sample.nmea
```

### Step 2: Convert to .fvc

```bash
# Convert NMEA to .fvc
fvc df --in sample.nmea convert nmea sample.fvc

# Check output
ls -la sample.fvc
cat sample.fvc
```

**Expected output**:
```
{"content": "flightlog", "source": "nmea", "origin": "sample.nmea"}
{"time": {"unix": 123456780}, "pos": {"loc": {"lat": 52.568723, "lon": 4.83539, "alt": 100.5}}
{"time": {"unix": 123457780}, "pos": {"loc": {"lat": 52.568733, "lon": 4.835407, "alt": 101.0}}
```

### Step 3: Validate the Output

```bash
# Validate
fvc df --in sample.fvc validate

# With verbose output
fvc df --in sample.fvc validate --verbose
```

**Expected output**:
```
✓ Validation successful
File: sample.fvc
Records: 3
Content type: flightlog
```

### Step 4: Analyze the Data

```bash
# Get statistics
fvc tools flightlog stats sample.fvc

# Get geoid undulation at sample location
fvc calc undulation 52.568723 4.83539

# Get terrain elevation
fvc calc terrain 52.568723 4.83539 100.5
```

### Step 5: Visualize the Flight

```bash
# Generate interactive HTML map
fvc render fl sample.fvc --output ./sample_map

# Open in browser
open ./sample_map/index.html
```

**What you'll see**:
- Interactive map showing flight path
- Waypoint markers
- Altitude/elevation profile
- Time-based playback

## Toolset Reference

fvctools is organized into toolsets:

### 1. Data File Tools (`fvc df`)

Convert, validate, and correlate aviation data files.

**Commands**:
- `convert` - Convert external format to .fvc
- `validate` - Validate .fvc file
- `correlate` - Correlate multiple .fvc files

**Examples**:
```bash
# Convert
fvc df flight.nmea convert nmea flight.fvc

# Validate
fvc df flight.fvc validate

# Correlate
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc
```

### 2. Geospatial Calculations (`fvc calc`)

Perform geospatial calculations.

**Commands**:
- `undulation` - Get EGM96 geoid undulation
- `terrain` - Get terrain elevation

**Examples**:
```bash
# Get geoid undulation
fvc calc undulation 52.3 4.9

# Get terrain elevation
fvc calc terrain 52.3 4.9 100.5
```

### 3. Visualization (`fvc render`)

Generate interactive visualizations.

**Commands**:
- `fl` - Generate flight map visualization

**Examples**:
```bash
# Generate HTML visualization
fvc render fl flight.fvc --output ./map

# Generate KML for GIS
fvc render fl flight.fvc --output flight.kml --format kml
```

## Common Use Cases

### Use Case 1: Batch Processing

```bash
# Convert all NMEA files in directory
for file in ./input/*.nmea; do
    output="./output/${file%.*}.fvc"
    fvc df --in "$file" convert nmea "$output"
    fvc df --in "$output" validate
done
```

### Use Case 2: Multi-Source Correlation

```bash
# Correlate flight and radar data
fvc df flight.fvc radar.fvc correlate --output fused.fvc

# Validate result
fvc df --in fused.fvc validate
```

### Use Case 3: Quality Control Pipeline

```bash
# Process, validate, and report
for file in ./raw/*.nmea; do
    output="./validated/${file%.*}.fvc"
    
    if fvc df --in "$file" convert nmea "$output" && \
       fvc df --in "$output" validate; then
        echo "✓ Valid: $file"
    else
        echo "✗ Invalid: $file"
    fi
done
```

### Use Case 4: Research Data Processing

```bash
# Full research pipeline
DATA_DIR="./research_data"
RESULTS_DIR="./results"

# Convert
fvc df --in "$DATA_DIR/flight.nmea" convert nmea "$RESULTS_DIR/flight.fvc"

# Validate
fvc df --in "$RESULTS_DIR/flight.fvc" validate

# Analyze
fvc tools flightlog stats "$RESULTS_DIR/flight.fvc" > "$RESULTS_DIR/stats.txt"

# Visualize
fvc render fl "$RESULTS_DIR/flight.fvc" --output "$RESULTS_DIR/map"

# Generate report
cat > "$RESULTS_DIR/report.md" << EOF
# Research Report

## Summary
Processed flight data from NMEA format.

## Statistics
$(cat "$RESULTS_DIR/stats.txt")

## Visualization
$RESULTS_DIR/map/
EOF
```

## Tips for Success

### 1. Always Validate Output

```bash
# Good practice
fvc df --in input.nmea convert nmea output.fvc
fvc df --in output.fvc validate
```

### 2. Use Verbose Mode for Debugging

```bash
fvc df --in input.nmea convert nmea output.fvc --verbose
```

### 3. Handle Errors Gracefully

```bash
# Check exit status
if fvc df --in input.nmea convert nmea output.fvc; then
    echo "Success!"
else
    echo "Conversion failed"
    exit 1
fi
```

### 4. Use Parallel Processing for Large Datasets

```bash
# Install GNU parallel
# Linux: sudo apt-get install parallel
# macOS: brew install parallel

# Parallel conversion
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc'
```

### 5. Document Your Workflows

```bash
# Create a README for your project
cat > README.md << 'EOF'
# My Flight Data Processing

## Workflow
1. Convert NMEA to .fvc
2. Validate output
3. Generate statistics
4. Create visualization

## Commands
```bash
fvc df --in flight.nmea convert nmea flight.fvc
fvc df --in flight.fvc validate
fvc tools flightlog stats flight.fvc
fvc render fl flight.fvc --output ./map
```

## Dependencies
- fvctools
- GNU parallel (for batch processing)
```
```

### 6. Use Environment Variables

```bash
# Set default values
export FVC_INPUT_DIR="./input"
export FVC_OUTPUT_DIR="./output"

# Use in commands
fvc df --in "$FVC_INPUT_DIR/flight.nmea" convert nmea "$FVC_OUTPUT_DIR/flight.fvc"
```

## Next Steps

Now that you've completed the quickstart, here are your next steps:

### 📖 Learn More

- **[Architecture Overview](/openwiki/architecture/overview.md)** - Understand how fvctools is structured
- **[Data Formats Guide](/openwiki/architecture/data-formats.md)** - Learn about .fvc format and supported formats
- **[CLI Tools Reference](/openwiki/architecture/tools.md)** - Complete reference for all CLI commands
- **[Development Setup](/openwiki/operations/setup.md)** - Set up for development
- **[Integration Guides](/openwiki/integrations/index.md)** - Learn about integrations with external libraries

### 🧪 Try These Exercises

1. **Convert a sample ULog file** (if available):
   ```bash
   fvc df sample.ulg convert ulog sample.fvc
   ```

2. **Validate the converted file**:
   ```bash
   fvc df sample.fvc validate
   ```

3. **Generate a visualization**:
   ```bash
   fvc render fl sample.fvc --output ./my_map
   ```

4. **Try batch processing**:
   ```bash
   mkdir -p input output
   # Copy some .nmea files to input/
   for file in ./input/*.nmea; do
       fvc df --in "$file" convert nmea "./output/${file%.*}.fvc"
   done
   ```

5. **Correlate two flight logs**:
   ```bash
   fvc df flight1.fvc flight2.fvc correlate --output merged.fvc
   ```

### 🔧 Advanced Topics

- **Polars Integration**: Learn about performance optimizations
- **Schema Validation**: Understand how data is validated
- **Custom Format Converters**: Add support for new formats
- **Performance Tuning**: Optimize for large datasets
- **Integration with Other Tools**: Connect fvctools to your data pipeline

## Troubleshooting

### Common Issues

#### Issue: Command not found

**Error**: `fvc: command not found`

**Solutions**:
```bash
# Check installation
which fvc

# Reinstall
uv pip install -e ".[dev]"
```

#### Issue: Module not found

**Error**: `ModuleNotFoundError: No module named 'fvc'`

**Solutions**:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install in development mode
uv pip install -e .
```

#### Issue: Conversion fails

**Error**: No output or error message

**Solutions**:
```bash
# Check input file
ls -la input.nmea

# Try verbose mode
fvc df --in input.nmea convert nmea output.fvc --verbose

# Check logs
cat fvctools.log 2>/dev/null || echo "No log file found"
```

#### Issue: Validation fails

**Error**: `ValidationError: <reason>`

**Solutions**:
```bash
# Check METADATA
head -n 1 output.fvc

# Validate with verbose output
fvc df --in output.fvc validate --verbose
```

## Resources

### Official Documentation

- **[Quickstart Guide](/openwiki/quickstart.md)** - This guide
- **[Architecture Overview](/openwiki/architecture/overview.md)** - System architecture
- **[Data Formats Guide](/openwiki/architecture/data-formats.md)** - .fvc format and supported formats
- **[CLI Tools Reference](/openwiki/architecture/tools.md)** - Complete CLI reference
- **[Development Setup](/openwiki/operations/setup.md)** - Set up for development
- **[Development Practices](/openwiki/operations/development.md)** - Best practices
- **[Integration Guides](/openwiki/integrations/index.md)** - External library integrations
- **[Testing Guide](/openwiki/testing/overview.md)** - Testing strategies

### Source Code

- **[GitHub Repository](https://github.com/flyvercity/fvctools)** - Source code and issues
- **[Schema Documentation](/docs/schema/README.md)** - Detailed schema documentation
- **[Test Files](/tests/)** - Example test files and data

### Community

- **Discussions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Wiki**: This OpenWiki documentation

## Getting Help

### Check Documentation First

```bash
# Check help for any command
fvc --help
fvc df --help
fvc df convert --help
fvc calc --help
fvc render --help
```

### Check Logs

```bash
# Check application logs
cat fvctools.log 2>/dev/null || echo "No log file"

# Check system logs (Linux)
journalctl -u fvctools -f
```

### Enable Debug Logging

```bash
export FVC_LOG_LEVEL=DEBUG
fvc df --in input.nmea convert nmea output.fvc
```

### Ask for Help

If you're still having issues:

1. Check the **[GitHub Issues](https://github.com/flyvercity/fvctools/issues)** page
2. Search for similar issues
3. Create a new issue with:
   - Error messages
   - Input file (if possible)
   - Steps to reproduce
   - Expected vs actual behavior

## Contributing

fvctools is an open-source project! Contributions are welcome.

### Ways to Contribute

1. **Report bugs** - Create GitHub issues
2. **Suggest features** - Open feature requests
3. **Add format converters** - Support new aviation formats
4. **Improve documentation** - Update this wiki
5. **Write tests** - Add test coverage
6. **Optimize performance** - Profile and optimize

### Development Setup

```bash
# Clone repository
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
ruff check src/fvc
ruff format src/fvc

# Run pre-commit hooks
pre-commit run --all-files
```

## Summary

You've completed the fvctools quickstart! 🎉

**You now know how to**:

✅ Install fvctools
✅ Convert external formats to .fvc
✅ Validate .fvc files
✅ Analyze flight data
✅ Generate visualizations
✅ Use the CLI tools
✅ Process data in batch

**Next steps**:

- Try converting your own data files
- Explore the architecture documentation
- Set up a development environment
- Contribute to the project

**Happy data processing!** 🚀

---

## Quick Reference Cheat Sheet

### Installation
```bash
git clone https://github.com/flyvercity/fvctools.git
cd fvctools
uv pip install -e ".[dev]"
fvc --version
```

### Basic Commands
```bash
# Convert
fvc df flight.nmea convert nmea flight.fvc

# Validate
fvc df flight.fvc validate

# Visualize
fvc render fl flight.fvc --output ./map

# Get undulation
fvc calc undulation 52.3 4.9

# Get terrain
fvc calc terrain 52.3 4.9 100.5
```

### Batch Processing
```bash
# Convert all files
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc'

# Validate all files
find ./output -name "*.fvc" | parallel -j $(nproc) 'fvc df {} validate'
```

### Quality Control
```bash
for file in ./raw/*.nmea; do
    output="./validated/${file%.*}.fvc"
    if fvc df --in "$file" convert nmea "$output" && \
       fvc df --in "$output" validate; then
        echo "✓ Valid: $file"
    else
        echo "✗ Invalid: $file"
    fi
done
```

### Research Pipeline
```bash
DATA_DIR="./research_data"
RESULTS_DIR="./results"

fvc df --in "$DATA_DIR/flight.nmea" convert nmea "$RESULTS_DIR/flight.fvc"
fvc df --in "$RESULTS_DIR/flight.fvc" validate
fvc tools flightlog stats "$RESULTS_DIR/flight.fvc" > "$RESULTS_DIR/stats.txt"
fvc render fl "$RESULTS_DIR/flight.fvc" --output "$RESULTS_DIR/map"
```

---

## 📚 Explore More

Ready to dive deeper? Check out these guides:

| Guide | Description |
|-------|-------------|
| **[Architecture Overview](/openwiki/architecture/overview.md)** | Learn how fvctools is structured |
| **[Data Formats Guide](/openwiki/architecture/data-formats.md)** | Master the .fvc format and supported formats |
| **[CLI Tools Reference](/openwiki/architecture/tools.md)** | Complete reference for all CLI commands |
| **[Development Setup](/openwiki/operations/setup.md)** | Set up your development environment |
| **[Integration Guides](/openwiki/integrations/index.md)** | Learn about external library integrations |
| **[Testing Guide](/openwiki/testing/overview.md)** | Write tests and ensure code quality |

---

**Welcome to the fvctools community!** 🎊

If you have questions, issues, or feature requests, don't hesitate to reach out.

Happy flying! ✈️