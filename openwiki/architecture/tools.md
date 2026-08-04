---
type: Tools Reference
title: CLI Tools Reference

description: Complete reference for all CLI tools in fvctools, including commands, options, and examples
resource: /src/fvc/tools/cli.py

tags: [cli, commands, tools, reference, fvc]
---

# CLI Tools Reference

This guide provides a complete reference for all **command-line tools** in fvctools, including commands, options, arguments, and usage examples.

## Overview

fvctools provides a **modular CLI** organized into toolsets:

- ✅ **`fvc df`** - Data File Tools (conversion, validation, correlation)
- ✅ **`fvc calc`** - Geospatial Calculations
- ✅ **`fvc render`** - Visualization Tools
- ✅ **Global options** - Common options for all commands

## Global Options

Options available for all fvc commands:

```
--version       Show version information and exit
--help, -h      Show help message and exit
--verbose, -v   Enable verbose output
--quiet, -q     Suppress non-essential output
--in <path>     Specify input file path (shortcut for --input)
--log-level <level>  Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

**Examples**:

```bash
# Show version
fvc --version

# Show help
fvc --help

# Show help for specific toolset
fvc df --help
fvc calc --help
fvc render --help

# Enable verbose output
fvc df --in input.nmea convert nmea output.fvc --verbose
```

## Toolset: fvc df (Data File Tools)

The `fvc df` toolset manages the conversion, validation, and correlation of aviation data files into the unified Flyvercity Data Format (`.fvc`).

### Commands

| Command | Description |
|---------|-------------|
| `convert` | Convert external format to .fvc |
| `validate` | Validate .fvc file against schema |
| `correlate` | Correlate multiple .fvc files |

### Common Options

```
--in, -i <path>      Input file path (can also be specified as first positional arg)
--output, -o <path>  Output file path (required for convert, optional for others)
--verbose, -v        Enable verbose output
--strict             Enable strict validation
```

---

## Command: fvc df convert

Convert external aviation data format to Flyvercity Data Format (.fvc).

### Usage

```bash
fvc df [--in <input_path>] convert <format> <output_path>

# Or with input as first positional argument
fvc df <input_path> convert <format> <output_path>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<format>` | string | Yes | Format to convert from (see supported formats below) |
| `<output_path>` | path | Yes | Path to output .fvc file |

### Options

```
--in, -i <path>      Input file path
--output, -o <path>  Output file path (can be specified here or as positional arg)
--verbose, -v        Enable verbose output
--help, -h           Show help message
```

### Supported Formats

| Format | Module | Description | Content Type |
|--------|--------|-------------|--------------|
| `nmea` | `nmea.py` | NMEA 0183 GPS protocol | flightlog |
| `ulog` | `ulog.py` | PX4 ULog format | flightlog |
| `safirmqtt` | `safirmqtt.py` | SAFIR MQTT v1 telemetry | flightlog |
| `safirmqtt_v2` | `safirmqtt_v2.py` | SAFIR MQTT v2 telemetry (optimized) | flightlog |
| `datcon` | `datcon.py` | DatCon flight recorder format | flightlog |
| `senhive` | `senhive.py` | SenHive flight logging system | flightlog |
| `agentfly` | `agentfly.py` | AgentFly simulator logs | flightlog |
| `artlog` | `artlog.py` | ART log format | flightlog |
| `courageous` | `courageous.py` | Courageous project logs | flightlog |
| `csgroup` | `csgroup.py` | CS Group radar logs | radarlog |
| `gnettrack` | `gnettrack.py` | G-NetTrack GPS logs | flightlog |
| `manna` | `manna.py` | Manna flight logs | flightlog |
| `robinradar` | `robinradar.py` | Robin Radar system logs | radarlog |
| `geojson` | `geojson.py` | GeoJSON geographic features | flightlog/radarlog |
| `kml` | `kml/` | KML Google Earth format | flightlog/radarlog |
| `fusion.replay` | - | Fusion engine replay events | fusion.replay |
| `capture.android` | - | Android MQTT capture | capture.message |

### Examples

#### Basic Conversion

```bash
# Convert NMEA to .fvc
fvc df --in flight.nmea convert nmea flight.fvc

# Or with positional arguments
fvc df flight.nmea convert nmea flight.fvc
```

#### Verbose Output

```bash
fvc df --in flight.nmea convert nmea flight.fvc --verbose
```

#### Batch Conversion

```bash
# Convert all NMEA files in directory
for file in ./input/*.nmea; do
    output="./output/${file%.*}.fvc"
    fvc df --in "$file" convert nmea "$output"
done
```

#### Parallel Batch Conversion

```bash
# Using GNU parallel
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc'
```

#### Streaming Conversion (SAFIR MQTT)

```bash
# From MQTT stream
mosquitto_sub -t "safir/telemetry" -v | \
python safir_converter.py

# Or directly
fvc df --in telemetry.json convert safirmqtt_v2 output.fvc
```

#### Format-Specific Examples

**NMEA Conversion**:

```bash
fvc df flight.nmea convert nmea flight.fvc
```

**ULog Conversion**:

```bash
fvc df flight.ulg convert ulog flight.fvc
```

**SAFIR MQTT Conversion**:

```bash
fvc df telemetry.json convert safirmqtt_v2 output.fvc
```

**DatCon Conversion**:

```bash
fvc df flight.datcon convert datcon flight.fvc
```

**SenHive Conversion**:

```bash
fvc df flight.senhive convert senhive flight.fvc
```

**AgentFly Conversion**:

```bash
fvc df flight.csv convert agentfly flight.fvc
```

**GeoJSON Conversion**:

```bash
fvc df features.geojson convert geojson output.fvc
```

**KML Conversion**:

```bash
fvc df features.kml convert kml output.fvc
```

### Error Handling

**Common Errors**:

```bash
# File not found
fvc df nonexistent.nmea convert nmea output.fvc
# Error: File not found: nonexistent.nmea

# Invalid format
fvc df flight.nmea convert invalid_format output.fvc
# Error: Unknown format: invalid_format

# Permission denied
fvc df /root/flight.nmea convert nmea output.fvc
# Error: Permission denied
```

**Solutions**:

```bash
# Check file exists
ls -la flight.nmea

# Check format name
fvc df convert --help

# Check permissions
ls -la /root/flight.nmea
```

### Performance Tips

```bash
# Use optimized converters (v2 where available)
fvc df telemetry.json convert safirmqtt_v2 output.fvc

# Use Polars-based converters for better performance
# agentfly, datcon, senhive converters are optimized with Polars

# For large files, ensure you have enough memory
# Consider streaming or chunking for very large files
```

---

## Command: fvc df validate

Validate a Flyvercity Data Format (.fvc) file against the schema.

### Usage

```bash
fvc df [--in <input_path>] validate [--output <output_path>]

# Or with input as first positional argument
fvc df <input_path> validate
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| (none) | - | No | Input file path (can be specified with --in or as positional arg) |

### Options

```
--in, -i <path>      Input file path
--output, -o <path>  Output validation report path (optional)
--verbose, -v        Enable verbose output (shows errors)
--strict             Enable strict validation
--help, -h           Show help message
```

### Examples

#### Basic Validation

```bash
# Validate .fvc file
fvc df --in flight.fvc validate

# Or with positional argument
fvc df flight.fvc validate
```

#### Verbose Validation

```bash
fvc df --in flight.fvc validate --verbose
```

#### Validation with Report

```bash
fvc df --in flight.fvc validate --output validation_report.txt
```

#### Batch Validation

```bash
# Validate all .fvc files
for file in ./output/*.fvc; do
    echo "Validating $file"
    fvc df --in "$file" validate || echo "Validation failed: $file"
done
```

#### CI/CD Validation

```bash
# In GitHub Actions
- name: Validate output
  run: |
    for file in ./output/*.fvc; do
      fvc df --in "$file" validate
    done
```

### Validation Output

**Success**:
```
✓ Validation successful
File: flight.fvc
Records: 1000
Content type: flightlog
```

**Failure**:
```
✗ Validation failed
File: flight.fvc
Error: ValidationError: 'time' is a required property
Line: 5
Record: {"pos": {"loc": {"lat": 52.3, "lon": 4.9}}
```

### Validation Modes

| Mode | Description |
|------|-------------|
| **Basic** | Checks METADATA and schema compliance |
| **Verbose** | Shows detailed error messages |
| **Strict** | Additional validation checks |

**Strict validation**:
```bash
fvc df --in flight.fvc validate --strict
```

### Common Validation Errors

#### 1. METADATA Errors

```
Error: METADATA is missing or invalid
Solution: Check first line of file
```

#### 2. Content Type Mismatch

```
Error: Content type mismatch
Expected: flightlog
Found: radarlog
Solution: Ensure METADATA content matches data records
```

#### 3. Missing Required Fields

```
Error: 'time' is a required property
Solution: Check data records for missing fields
```

#### 4. Invalid Field Types

```
Error: 123 is not of type 'string'
Solution: Check field types match schema
```

#### 5. Range Violations

```
Error: 100 is greater than the maximum of 90
Field: lat
Solution: Check latitude is between -90 and 90
```

### Performance Tips

```bash
# For batch validation, use parallel processing
find ./output -name "*.fvc" | parallel -j $(nproc) fvc df {} validate

# Use --quiet to suppress output for automation
fvc df --in flight.fvc validate --quiet
```

---

## Command: fvc df correlate

Correlate and merge multiple .fvc files into a single output file.

### Usage

```bash
fvc df [--in <input1> <input2> ...] correlate --output <output_path>

# Or with input files as positional arguments
fvc df <input1> <input2> ... correlate --output <output_path>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<input_files>` | paths | Yes | Two or more .fvc files to correlate |
| `--output, -o` | path | Yes | Output file path |

### Options

```
--in, -i <path>      Input file path(s)
--output, -o <path>  Output file path (required)
--verbose, -v        Enable verbose output
--method <method>    Correlation method (default: timestamp)
--help, -h           Show help message
```

### Examples

#### Basic Correlation

```bash
# Correlate two flight logs
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc

# Or with --in option
fvc df --in flight1.fvc flight2.fvc correlate --output merged.fvc
```

#### Correlation with Validation

```bash
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc && \
fvc df --in merged.fvc validate
```

#### Correlation with Multiple Files

```bash
# Correlate three or more files
fvc df flight1.fvc flight2.fvc flight3.fvc correlate --output all_flights.fvc
```

#### Flight + Radar Correlation

```bash
# Correlate flight and radar data
fvc df flight.fvc radar.fvc correlate --output fused.fvc
```

#### Verbose Correlation

```bash
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc --verbose
```

### Correlation Process

The correlation engine:

1. **Parses all input files**
2. **Aligns records by timestamp** (default method)
3. **Merges overlapping or adjacent records**
4. **Handles gaps and mismatches**
5. **Writes merged output**

### Correlation Methods

| Method | Description |
|--------|-------------|
| `timestamp` (default) | Align by Unix timestamp |
| `spatial` | Align by geographic proximity |
| `hybrid` | Combine timestamp and spatial alignment |

**Specify method**:
```bash
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc --method timestamp
```

### Use Cases

#### 1. Multi-Source Flight Data

```bash
# Combine flight logs from multiple devices
fvc df drone1.fvc drone2.fvc drone3.fvc correlate --output combined.fvc
```

#### 2. Flight + Radar Correlation

```bash
# Synchronize radar detections with flight paths
fvc df flight.fvc radar.fvc correlate --output fused.fvc
```

#### 3. Temporal Alignment

```bash
# Handle clock drift between systems
fvc df system1.fvc system2.fvc correlate --output aligned.fvc
```

#### 4. Spatial Alignment

```bash
# Match observations in geographic space
fvc df observation1.fvc observation2.fvc correlate --output spatial.fvc
```

### Error Handling

**Common Errors**:

```bash
# Not enough input files
fvc df flight1.fvc correlate --output output.fvc
# Error: At least 2 input files required

# Files have incompatible content types
fvc df flight.fvc radar.fvc correlate --output output.fvc
# Error: Content type mismatch (flightlog vs radarlog)

# Output file already exists
fvc df flight1.fvc flight2.fvc correlate --output output.fvc
# Error: Output file exists
```

**Solutions**:

```bash
# Check number of input files
ls -1 *.fvc | wc -l

# Check content types
head -n 1 *.fvc

# Remove existing output
rm -f output.fvc
```

### Performance Tips

```bash
# For large files, ensure you have enough memory
# Correlation requires loading all data into memory

# Use --verbose to monitor progress
fvc df large1.fvc large2.fvc correlate --output merged.fvc --verbose
```

---

## Toolset: fvc calc (Geospatial Calculations)

The `fvc calc` toolset provides utilities for precise geospatial calculations, including geoid undulation and terrain elevation lookups.

### Commands

| Command | Description |
|---------|-------------|
| `undulation` | Get EGM96 geoid undulation |
| `terrain` | Get terrain elevation |

### Common Options

```
--help, -h      Show help message
--verbose, -v   Enable verbose output
```

---

## Command: fvc calc undulation

Get the EGM96 geoid undulation at given coordinates.

### Usage

```bash
fvc calc undulation <latitude> <longitude>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<latitude>` | float | Yes | Latitude in decimal degrees (WGS-84) |
| `<longitude>` | float | Yes | Longitude in decimal degrees (WGS-84) |

### Options

```
--help, -h      Show help message
--verbose, -v   Enable verbose output
```

### Examples

#### Basic Usage

```bash
# Get undulation at Amsterdam coordinates
fvc calc undulation 52.3 4.9

# Output:
# Undulation: 48.2 meters
# AMSL altitude = ellipsoidal altitude - undulation
```

#### Script Usage

```bash
# Calculate AMSL altitude
AMSL=$(echo "$ELLIP_ALT - $(fvc calc undulation $LAT $LON)" | bc)
echo "AMSL altitude: $AMSL meters"
```

#### Batch Processing

```bash
# Process multiple coordinates
while read lat lon; do
    undulation=$(fvc calc undulation $lat $lon)
    echo "$lat,$lon,$undulation"
done < coordinates.txt
```

### Output Format

```
Undulation: <value> meters
```

**Example output**:
```
Undulation: 48.2 meters
```

### Use Cases

#### 1. Altitude Conversion

```bash
# Convert ellipsoidal altitude to AMSL
ELLIP_ALT=100.5
LAT=52.3
LON=4.9

AMSL=$(echo "$ELLIP_ALT - $(fvc calc undulation $LAT $LON)" | bc)
echo "AMSL: $AMSL meters"
```

#### 2. Flight Data Processing

```bash
# Process flight log and convert altitudes
while read lat lon alt; do
    undulation=$(fvc calc undulation $lat $lon)
    amsl=$(echo "$alt - $undulation" | bc)
    echo "$lat,$lon,$alt,$amsl"
done < flight_data.txt
```

### Error Handling

**Common Errors**:

```bash
# Invalid coordinates (out of range)
fvc calc undulation 100 200
# Error: Latitude must be between -90 and 90
# Longitude must be between -180 and 180
```

**Solutions**:

```bash
# Check coordinates
fvc calc undulation 52.3 4.9  # Valid
fvc calc undulation -90 -180   # Valid (boundary)
fvc calc undulation 91 0       # Invalid (latitude too high)
```

---

## Command: fvc calc terrain

Get terrain elevation at given coordinates and altitude.

### Usage

```bash
fvc calc terrain <latitude> <longitude> <altitude>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<latitude>` | float | Yes | Latitude in decimal degrees (WGS-84) |
| `<longitude>` | float | Yes | Longitude in decimal degrees (WGS-84) |
| `<altitude>` | float | Yes | Altitude in meters (AMSL) |

### Options

```
--help, -h      Show help message
--verbose, -v   Enable verbose output
```

### Examples

#### Basic Usage

```bash
# Get terrain elevation at Amsterdam
fvc calc terrain 52.3 4.9 100.5

# Output:
# Terrain elevation: 52.3 meters AMSL
# Height above ground: 48.2 meters
```

#### Flight Data Processing

```bash
# Process flight log and calculate height above ground
while read lat lon alt; do
    terrain=$(fvc calc terrain $lat $lon $alt)
    height=$(echo "$alt - $terrain" | bc)
    echo "$lat,$lon,$alt,$terrain,$height"
done < flight_data.txt
```

### Output Format

```
Terrain elevation: <value> meters AMSL
Height above ground: <value> meters
```

**Example output**:
```
Terrain elevation: 52.3 meters AMSL
Height above ground: 48.2 meters
```

### Use Cases

#### 1. Terrain Following

```bash
# Calculate safe altitude above terrain
MIN_CLEARANCE=50  # meters

while read lat lon alt; do
    terrain=$(fvc calc terrain $lat $lon $alt)
    clearance=$(echo "$alt - $terrain" | bc)
    
    if (( $(echo "$clearance < $MIN_CLEARANCE" | bc -l) )); then
        echo "WARNING: Low clearance at $lat,$lon: $clearance meters"
    fi
done < flight_path.txt
```

#### 2. Obstacle Detection

```bash
# Check for obstacles
MAX_SAFE_ALTITUDE=150  # meters

while read lat lon alt; do
    terrain=$(fvc calc terrain $lat $lon $alt)
    
    if (( $(echo "$alt - $terrain < $MAX_SAFE_ALTITUDE" | bc -l) )); then
        echo "Potential obstacle at $lat,$lon"
    fi
done < flight_data.txt
```

### Error Handling

**Common Errors**:

```bash
# Missing DEM data for location
fvc calc terrain 0 0 100
# Error: No DEM data available for this location

# Invalid coordinates
fvc calc terrain 100 200 100
# Error: Coordinates out of range
```

**Solutions**:

```bash
# Check DEM coverage
# Ensure DEM files are available

# Use coordinates with DEM coverage
fvc calc terrain 52.3 4.9 100  # Amsterdam has DEM data
```

---

## Toolset: fvc render (Visualization)

The `fvc render` toolset generates interactive visualizations for flight and radar data analysis.

### Commands

| Command | Description |
|---------|-------------|
| `fl` | Generate interactive flight map visualization |

### Common Options

```
--output, -o <path>  Output directory path (required)
--format <format>    Output format: html, kml, json (default: html)
--title <title>      Visualization title
--description <desc> Visualization description
--verbose, -v        Enable verbose output
--help, -h           Show help message
```

---

## Command: fvc render fl

Generate an interactive flight map visualization from .fvc flight data.

### Usage

```bash
fvc render fl [--in <input_path>] --output <output_dir> [--format <format>]

# Or with input as first positional argument
fvc render fl <input_path> --output <output_dir> [--format <format>]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<input_path>` | path | Yes | Path to input .fvc flight file |

### Options

```
--in, -i <path>      Input file path
--output, -o <path>  Output directory path (required)
--format <format>    Output format: html, kml, json (default: html)
--title <title>      Visualization title
--description <desc> Visualization description
--verbose, -v        Enable verbose output
--help, -h           Show help message
```

### Examples

#### Basic Visualization

```bash
# Generate interactive HTML map
fvc render fl flight.fvc --output ./flight_map

# Open the visualization
open ./flight_map/index.html
```

#### KML Export for GIS

```bash
# Generate KML for Google Earth
fvc render fl flight.fvc --output flight.kml --format kml

# Open in Google Earth
open flight.kml
```

#### JSON Export for Analysis

```bash
# Export data in JSON format
fvc render fl flight.fvc --output flight_data.json --format json
```

#### Custom Title and Description

```bash
fvc render fl flight.fvc --output ./map \
  --title "Amsterdam Flight Test" \
  --description "Flight test on 2025-04-25"
```

#### Verbose Output

```bash
fvc render fl flight.fvc --output ./map --verbose
```

### Output Formats

| Format | Description | File Extension | Usage |
|--------|-------------|----------------|-------|
| **HTML** | Interactive map with Leaflet.js | `.html` (directory) | Web browser |
| **KML** | Google Earth format | `.kml` | Google Earth, QGIS |
| **JSON** | Raw data export | `.json` | Programmatic analysis |

### HTML Visualization Features

**Interactive HTML maps include**:

- ✅ Interactive map with Leaflet.js
- ✅ Flight path visualization
- ✅ Waypoint markers
- ✅ Altitude/elevation profile
- ✅ Time-based playback
- ✅ Zoom and pan controls
- ✅ Responsive design
- ✅ Mobile-friendly

**Example HTML structure**:
```
flight_map/
├── index.html          # Main visualization page
├── flight_path.geojson # Flight path data
├── config.json         # Visualization configuration
└── assets/             # CSS, JS, images
```

### KML Visualization Features

**KML output includes**:

- ✅ Compatible with Google Earth
- ✅ Compatible with QGIS, ArcGIS
- ✅ Geographic coordinates
- ✅ Altitude information
- ✅ Placemark styling
- ✅ Path visualization

**Example KML structure**:
```xml
<kml>
  <Document>
    <name>Flight Map</name>
    <Placemark>
      <name>Flight Path</name>
      <LineString>
        <coordinates>4.9,52.3,100 4.9001,52.3001,100.5</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>
```

### JSON Visualization Features

**JSON output includes**:

- ✅ Raw flight data
- ✅ Easy to parse programmatically
- ✅ Can be re-imported into .fvc format
- ✅ Flight path coordinates
- ✅ Metadata

**Example JSON structure**:
```json
{
  "title": "Flight Map",
  "description": "Flight test",
  "flight_path": [
    {"lat": 52.3, "lon": 4.9, "alt": 100.5},
    {"lat": 52.3001, "lon": 4.9001, "alt": 100.8}
  ],
  "metadata": {
    "source": "nmea",
    "records": 1000
  }
}
```

### Use Cases

#### 1. Flight Analysis

```bash
# Convert, validate, and visualize
fvc df --in flight.nmea convert nmea flight.fvc && \
fvc df --in flight.fvc validate && \
fvc render fl flight.fvc --output ./analysis

# Open results
open ./analysis/index.html
```

#### 2. Batch Visualization

```bash
# Generate visualizations for all flight logs
for file in ./flights/*.fvc; do
    output="./maps/${file%.*}"
    fvc render fl "$file" --output "$output"
done
```

#### 3. GIS Integration

```bash
# Export to KML for GIS software
fvc render fl flight.fvc --output flight.kml --format kml

# Import into QGIS
qgis flight.kml
```

#### 4. Web Integration

```bash
# Serve visualization on web server
python -m http.server 8000 --directory ./flight_map
# Access at http://localhost:8000
```

### Customization

#### Custom Title

```bash
fvc render fl flight.fvc --output ./map --title "My Flight"
```

#### Custom Description

```bash
fvc render fl flight.fvc --output ./map \
  --description "Flight test on 2025-04-25 with weather data"
```

#### Multiple Output Formats

```bash
# Generate HTML visualization
fvc render fl flight.fvc --output ./html_map --format html

# Generate KML for GIS
fvc render fl flight.fvc --output ./kml_map.kml --format kml

# Generate JSON for analysis
fvc render fl flight.fvc --output flight_data.json --format json
```

### Error Handling

**Common Errors**:

```bash
# Input file not found
fvc render fl nonexistent.fvc --output ./map
# Error: File not found

# Invalid .fvc file
fvc render fl invalid.fvc --output ./map
# Error: Validation failed

# Output directory doesn't exist
fvc render fl flight.fvc --output /nonexistent/map
# Error: Output directory doesn't exist
```

**Solutions**:

```bash
# Check file exists
ls -la flight.fvc

# Validate input first
fvc df --in flight.fvc validate

# Create output directory
mkdir -p ./map
```

### Performance Tips

```bash
# For large flight logs:
# - Use HTML format for interactive exploration
# - Use KML format for GIS integration
# - Use JSON format for programmatic analysis

# For very large files, consider:
# - Downsampling data
# - Using chunked processing
# - Generating previews
```

---

## Advanced Usage Patterns

### 1. Conversion Pipeline

```bash
# Full pipeline: Convert → Validate → Analyze → Visualize
fvc df --in flight.nmea convert nmea flight.fvc && \
fvc df --in flight.fvc validate && \
fvc tools flightlog stats flight.fvc > stats.txt && \
fvc render fl flight.fvc --output ./analysis
```

### 2. Batch Processing

```bash
# Convert all files in directory
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc && \
   fvc df --in {.}.fvc validate'
```

### 3. Automated Workflow

```bash
#!/bin/bash
# auto_process.sh - Automated data processing workflow

INPUT_DIR="./incoming"
PROCESSED_DIR="./processed"
mkdir -p "$PROCESSED_DIR"

# Watch for new files
inotifywait -m -e create -e moved_to --format '%f' "$INPUT_DIR" | \
while read NEW_FILE; do
    echo "$(date): Processing $NEW_FILE"
    
    # Determine format
    if [[ "$NEW_FILE" == *.nmea ]]; then
        FORMAT="nmea"
    elif [[ "$NEW_FILE" == *.ulg ]]; then
        FORMAT="ulog"
    else
        echo "$(date): Unknown format: $NEW_FILE"
        continue
    fi
    
    OUTPUT="$PROCESSED_DIR/${NEW_FILE%.*}.fvc"
    
    # Convert
    if fvc df --in "$INPUT_DIR/$NEW_FILE" convert "$FORMAT" "$OUTPUT"; then
        # Validate
        if fvc df --in "$OUTPUT" validate; then
            echo "$(date): ✓ Success: $NEW_FILE"
            mv "$INPUT_DIR/$NEW_FILE" "$PROCESSED_DIR/"
        else
            echo "$(date): ✗ Validation failed: $OUTPUT"
        fi
    else
        echo "$(date): ✗ Conversion failed: $NEW_FILE"
    fi
done
```

### 4. Quality Control Pipeline

```bash
#!/bin/bash
# quality_control.sh

INPUT_DIR="./raw"
OUTPUT_DIR="./validated"
REJECT_DIR="./rejected"
mkdir -p "$OUTPUT_DIR" "$REJECT_DIR"

process_file() {
    local file="$1"
    local base_name=$(basename "${file%.*}")
    local output="$OUTPUT_DIR/${base_name}.fvc"
    local reject="$REJECT_DIR/${base_name}.rej"
    
    echo "Processing: $file"
    
    # Convert
    if fvc df --in "$file" convert nmea "$output" 2>/dev/null; then
        # Validate
        if fvc df --in "$output" validate 2>/dev/null; then
            echo "✓ Valid: $file"
            return 0
        else
            echo "✗ Invalid: $file"
            mv "$output" "$reject"
            return 1
        fi
    else
        echo "✗ Conversion failed: $file"
        return 1
    fi
}

# Process all files
for file in "$INPUT_DIR"/*.nmea; do
    [ -f "$file" ] && process_file "$file"
done

# Generate report
valid_count=$(ls "$OUTPUT_DIR"/*.fvc 2>/dev/null | wc -l)
invalid_count=$(ls "$REJECT_DIR"/*.rej 2>/dev/null | wc -l)

cat > quality_report.txt << EOF
Quality Control Report
=====================

Processed: $(ls "$INPUT_DIR"/*.nmea 2>/dev/null | wc -l) files
Valid: $valid_count files
Invalid: $invalid_count files
Success Rate: $((valid_count * 100 / ($(ls "$INPUT_DIR"/*.nmea 2>/dev/null | wc -l) + 1)))%

Valid files: $OUTPUT_DIR/
Invalid files: $REJECT_DIR/
EOF

echo "Quality control complete. Report: quality_report.txt"
```

### 5. Research Data Processing

```bash
#!/bin/bash
# research_pipeline.sh

DATA_DIR="./research_data"
RESULTS_DIR="./results"
mkdir -p "$RESULTS_DIR"

# Step 1: Convert all data to .fvc
for file in "$DATA_DIR"/*.nmea; do
    output="$RESULTS_DIR/$(basename "${file%.*}.fvc")"
    fvc df --in "$file" convert nmea "$output"
done

# Step 2: Validate all converted files
for file in "$RESULTS_DIR"/*.fvc; do
    fvc df --in "$file" validate || exit 1
done

# Step 3: Generate statistics
fvc tools flightlog stats "$RESULTS_DIR/flight.fvc" > "$RESULTS_DIR/stats.txt"

# Step 4: Create visualizations
fvc render fl "$RESULTS_DIR/flight.fvc" --output "$RESULTS_DIR/flight_map"

# Step 5: Generate report
cat > "$RESULTS_DIR/report.md" << EOF
# Research Data Analysis Report

## Summary
- Files processed: X
- Validation: Passed
- Key findings: Y

## Statistics
$(cat "$RESULTS_DIR/stats.txt")

## Visualizations
- Flight map: $RESULTS_DIR/flight_map/

## Recommendations
Z
EOF

echo "Research pipeline complete. Results in: $RESULTS_DIR/"
```

---

## Tips and Tricks

### 1. Use Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias fvc-convert='fvc df convert'
alias fvc-validate='fvc df validate'
alias fvc-correlate='fvc df correlate'

# Usage
fvc-convert flight.nmea nmea flight.fvc
```

### 2. Use Environment Variables

```bash
# Set default values
export FVC_INPUT_DIR="./input"
export FVC_OUTPUT_DIR="./output"

# Use in commands
fvc df --in "$FVC_INPUT_DIR/flight.nmea" convert nmea "$FVC_OUTPUT_DIR/flight.fvc"
```

### 3. Use Makefile for Common Tasks

```makefile
# Makefile

INPUT ?= flight.nmea
OUTPUT ?= flight.fvc
MAP_DIR ?= map_results

all: validate visualize

convert:
	@echo "Converting $(INPUT) to $(OUTPUT)"
	fvc df --in $(INPUT) convert nmea $(OUTPUT)

validate: convert
	@echo "Validating $(OUTPUT)"
	fvc df --in $(OUTPUT) validate

visualize: validate
	@echo "Generating visualization"
	fvc render fl $(OUTPUT) --output $(MAP_DIR)

clean:
	rm -rf $(OUTPUT) $(MAP_DIR)

.PHONY: all convert validate visualize clean
```

**Usage**:
```bash
make convert
make validate
make visualize
```

### 4. Use jq for JSON Processing

```bash
# Extract flight path
fvc render fl flight.fvc --output flight.json --format json
cat flight.json | jq '.flight_path[] | "\(.lat),\(.lon),\(.alt)"' > path.csv

# Process with jq
cat flight.json | jq '.metadata' > metadata.json
```

### 5. Use Parallel Processing

```bash
# Install GNU parallel
# Linux: sudo apt-get install parallel
# macOS: brew install parallel

# Parallel conversion
find ./input -name "*.nmea" | parallel -j $(nproc) \
  'fvc df --in {} convert nmea {.}.fvc'

# Parallel validation
find ./output -name "*.fvc" | parallel -j $(nproc) \
  'fvc df --in {} validate'
```

### 6. Use tmux/screen for Long-running Jobs

```bash
# Start tmux session
tmux new -s fvc_job

# Run long job
fvc df --in large.nmea convert nmea large.fvc

# Detach from session
Ctrl+B, D

# Reattach later
tmux attach -t fvc_job
```

---

## Troubleshooting CLI Issues

### 1. Command Not Found

**Error**: `fvc: command not found`

**Solutions**:

```bash
# Check installation
which fvc

# Check Python environment
python -c "import fvc; print(fvc.__file__)"

# Reinstall
uv pip install -e ".[dev]"
```

### 2. Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fvc'`

**Solutions**:

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install in development mode
uv pip install -e .

# Check pyproject.toml
cat pyproject.toml | grep "name ="
```

### 3. Permission Denied

**Error**: `Permission denied`

**Solutions**:

```bash
# Check file permissions
ls -la /path/to/file

# Check directory permissions
ls -la /path/to/dir

# Use absolute paths
fvc df /absolute/path/to/file.nmea convert nmea /absolute/path/to/output.fvc
```

### 4. Format Not Supported

**Error**: `ValueError: Unknown format: xxx`

**Solutions**:

```bash
# Check supported formats
fvc df convert --help

# Check format name spelling
fvc df flight.nmea convert nmea output.fvc

# Add format converter if needed
```

### 5. Memory Issues

**Error**: `MemoryError` or `Out of memory`

**Solutions**:

```bash
# Use streaming where possible
# Process in chunks
# Use Polars with lazy evaluation
# Increase system memory
```

---

## Best Practices

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

### 3. Document Your Workflows

```bash
# Create a README for your workflow
cat > workflow_readme.md << EOF
# My Data Processing Workflow

## Overview
Process flight data from NMEA to visualization.

## Steps
1. Convert NMEA to .fvc
2. Validate .fvc file
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
- jq (for JSON processing)
```
```

### 4. Use Version Control

```bash
# Commit your workflows
git add workflow.sh
git commit -m "Add data processing workflow"
```

### 5. Automate Repetitive Tasks

```bash
# Use Makefile
make convert
make validate
make visualize

# Use shell scripts
./process_data.sh

# Use cron for scheduled tasks
0 2 * * * /opt/fvctools/process_daily.sh
```

### 6. Monitor Resource Usage

```bash
# Check memory usage
top -o %MEM

# Check disk usage
df -h

# Check CPU usage
mpstat -P ALL 1
```

### 7. Handle Errors Gracefully

```bash
# Check exit status
if fvc df --in input.nmea convert nmea output.fvc; then
    echo "Success"
else
    echo "Failed"
    exit 1
fi

# Use set -e in scripts
set -euo pipefail
```

### 8. Use Appropriate Data Types

```bash
# For coordinates, use Float32 instead of Float64
# Saves 50% memory

# In Polars:
pl.Float32()  # Instead of pl.Float64()
```

### 9. Test with Real Data

```bash
# Always test with real data before deployment
# Verify conversion logic
# Check output quality
```

### 10. Document Assumptions

```markdown
# Assumptions
- Input files are in NMEA format
- Altitude is in meters
- Coordinates are in WGS-84
- Timestamps are Unix time in milliseconds

# Known Issues
- Doesn't handle NMEA sentences with missing fields
- Limited to 1000 records per file
```

---

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Architecture Overview](/openwiki/architecture/overview.md)
- [Data Formats Guide](/openwiki/architecture/data-formats.md)
- [Development Setup](/openwiki/operations/setup.md)
- [Development Practices](/openwiki/operations/development.md)
- [Testing Guide](/openwiki/testing/overview.md)

## Quick Reference

| Command | Usage | Description |
|---------|-------|-------------|
| `fvc --version` | `fvc --version` | Show version |
| `fvc --help` | `fvc --help` | Show help |
| `fvc df convert` | `fvc df convert <format> <output>` | Convert format |
| `fvc df validate` | `fvc df validate` | Validate .fvc file |
| `fvc df correlate` | `fvc df file1.fvc file2.fvc correlate --output out.fvc` | Correlate files |
| `fvc calc undulation` | `fvc calc undulation 52.3 4.9` | Get geoid undulation |
| `fvc calc terrain` | `fvc calc terrain 52.3 4.9 100.5` | Get terrain elevation |
| `fvc render fl` | `fvc render fl flight.fvc --output map` | Generate visualization |

## Cheat Sheet

### Data Conversion
```bash
# NMEA
fvc df flight.nmea convert nmea flight.fvc

# ULog
fvc df flight.ulg convert ulog flight.fvc

# SAFIR MQTT
fvc df telemetry.json convert safirmqtt_v2 output.fvc

# Batch conversion
find ./input -name "*.nmea" | parallel -j $(nproc) 'fvc df {} convert nmea {.}.fvc'
```

### Validation
```bash
# Validate single file
fvc df flight.fvc validate

# Validate with verbose output
fvc df flight.fvc validate --verbose

# Batch validation
find ./output -name "*.fvc" | parallel -j $(nproc) 'fvc df {} validate'
```

### Correlation
```bash
# Correlate two files
fvc df flight1.fvc flight2.fvc correlate --output merged.fvc

# Correlate multiple files
fvc df *.fvc correlate --output all.fvc
```

### Calculations
```bash
# Geoid undulation
fvc calc undulation 52.3 4.9

# Terrain elevation
fvc calc terrain 52.3 4.9 100.5
```

### Visualization
```bash
# HTML visualization
fvc render fl flight.fvc --output ./map

# KML for GIS
fvc render fl flight.fvc --output flight.kml --format kml

# JSON export
fvc render fl flight.fvc --output flight.json --format json
```

### Quality Control
```bash
# Convert and validate
fvc df --in input.nmea convert nmea output.fvc && \
fvc df --in output.fvc validate

# Batch quality control
for file in ./input/*.nmea; do
    fvc df --in "$file" convert nmea "${file%.*}.fvc" && \
    fvc df --in "${file%.*}.fvc" validate || echo "Failed: $file"
done
```

---

## Next Steps

- **Try the CLI**: Run `fvc --help` to see all options
- **Convert sample data**: Try converting a sample NMEA file
- **Validate output**: Always validate your .fvc files
- **Explore visualizations**: Generate a map from your flight data
- **Read architecture guide**: [/openwiki/architecture/overview.md](/openwiki/architecture/overview.md)
- **Check data formats**: [/openwiki/architecture/data-formats.md](/openwiki/architecture/data-formats.md)
