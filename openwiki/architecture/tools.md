---
type: Tools Reference
title: CLI Tools Reference

description: Complete reference for all CLI commands and options across fvc df, fvc calc, fvc render, and global options. Includes examples and argument details.
resource: /src/fvc/tools/cli.py

tags: [cli, commands, tools, reference, fvc, df, calc, render]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T12:24:16.401Z
sources:
  - id: openwiki-source-3dd122e5fe934502061804bf
    resource: repo://src/fvc/tools/calc/cli.py
  - id: openwiki-source-d89fcd3fc5cba86004bd8f31
    resource: repo://src/fvc/tools/cli.py
  - id: openwiki-source-5ed15730fa37741e976035a2
    resource: repo://src/fvc/tools/df/cli.py
  - id: openwiki-source-0f3169a0fad1c9bd3012c9a6
    resource: repo://src/fvc/tools/df/fusion.py
  - id: openwiki-source-9f7669744943af02638a377e
    resource: repo://src/fvc/tools/flightlog/cli.py
  - id: openwiki-source-e8dbd945884f7fd08dd33282
    resource: repo://src/fvc/tools/render/cli.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T12:24:16.401Z" }
---

# CLI Tools Reference

This guide provides a **complete reference** for all **command-line tools** in fvctools, including commands, options, arguments, and usage examples.

## Overview

fvctools provides a **modular CLI** organized into toolsets:

- ✅ **`fvc df`** – Data File Tools (conversion, validation, correlation, export)
- ✅ **`fvc calc`** – Geospatial Calculations (epoch conversion, geoid undulation, terrain elevation)
- ✅ **`fvc render`** – Visualization Tools (flight log map generation)
- ✅ **Global options** – Common options for all commands

## Global Options

Options available for all fvc commands:

```
--version       Show version information and exit
--help, -h      Show help message and exit
--verbose, -v   Enable verbose output (debug logging)
--json          Make JSON default output format instead of free form
--no-pprint     Disable colored pretty printing
--aws-profile   AWS profile to use for S3 operations
--egm <path>    Custom EGM geoid data file (*.pgm). Default: egm96-5.pgm
```

**Examples**:

```bash
# Show version
fvc --version

# Show help for all commands
fvc --help

# Show help for specific toolset
fvc df --help
fvc calc --help
fvc render --help

# Enable verbose output
fvc df --in input.nmea convert nmea output.fvc --verbose

# Use JSON output format
fvc calc undulation 45.5 -73.2 --json
```

## Toolset: fvc df (Data File Tools)

The `fvc df` toolset manages the conversion, validation, correlation, and export of aviation data files into and from the unified Flyvercity Data Format (`.fvc`).

### Global Options for fvc df

```
--cache-dir <path>  Directory for caching external data (env: FVC_CACHE)
--in <path>, -i <path>  Input file path (can also be specified as first positional arg)
--suffix <suffix>   Suffix substitution for input files
--verbose, -v       Enable verbose output
--json              Make JSON default output format
--no-pprint         Disable colored pretty printing
```

### Commands

| Command | Description |
|---------|-------------|
| `convert` | Convert external format to `.fvc` |
| `export` | Convert `.fvc` data to an external format |
| `validate` | Validate `.fvc` file against schema |
| `correlate` | Correlate multiple `.fvc` files |
| `help` | Show help for a specific external format |
| `flightlog` | Flight log specific tools (subcommands) |
| `fusion` | SAFIR Fusion data extraction tools (subcommands) |

---

### Command: fvc df convert

Convert external aviation data format to Flyvercity Data Format (`.fvc`).

#### Usage

```bash
# Basic conversion (output inferred from input)
fvc df [--in <input_path>] convert <format> [<output_path>]

# With explicit output path
fvc df <input_path> convert <format> <output_path>

# Using global --in option
fvc df --in input.nmea convert nmea output.fvc
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<format>` | string | Yes | Format to convert from (see supported formats below) |
| `<output_path>` | path | No | Path to output `.fvc` file (inferred from input if omitted) |

#### Options

```
--target <type>     Target content type (choices: flightlog, radarlog), default: flightlog
--custom <param>    Custom parameters for the conversion (can be specified multiple times)
                    Use "fvc df help <format>" to see format-specific parameters
```

#### Supported Formats

- `agentfly` – AgentFly format
- `artlog` – ART format
- `courageous` – Courageous format
- `datcon` – DataConek format
- `gnettrack` – G-NetTrack format
- `nmea` – NMEA format
- `robinradar` – Robin Radar format
- `safirmqtt` – SAFIR MQTT format
- `senhive` – SenHive format
- `ulog` – ULog format

#### Examples

```bash
# Convert NMEA file to FVC
fvc df input.nmea convert nmea output.fvc

# Convert NMEA with explicit output path
fvc df --in input.nmea convert nmea

# Convert SAFIR MQTT with custom parameters
fvc df input.json convert safirmqtt output.fvc --custom param1=value1 --custom param2=value2

# Convert with verbose output
fvc df input.artlog convert artlog output.fvc --verbose
```

---

### Command: fvc df export

Convert Flyvercity Data Format (`.fvc`) to an external format.

#### Usage

```bash
fvc df export <format> [<output_path>]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<format>` | string | Yes | Format to export to |
| `<output_path>` | path | No | Output file path |

#### Examples

```bash
# Export FVC to JSON Lines
fvc df export frames output.jsonl

# Export with explicit output path
fvc df export nmea trajectory.nmea
```

---

### Command: fvc df validate

Validate a `.fvc` file against the known schema.

#### Usage

```bash
fvc df validate <input_path>
# or
fvc df --in <input_path> validate
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<input_path>` | path | Yes | Path to the `.fvc` file to validate |

#### Output

- Prints validation result: "Validation succeeded" or "Validation failed"
- Shows progress bar during validation
- In JSON mode, outputs: `{"valid": true/false}`

#### Examples

```bash
# Validate a flight log
fvc df validate flight.fvc

# Validate with verbose output
fvc df --in flight.fvc validate --verbose

# Get JSON output
fvc df flight.fvc validate --json
```

---

### Command: fvc df correlate

Correlate several flight log files to align timestamps and data points.

#### Usage

```bash
fvc df correlate <file1> [<file2> ...]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<file1>`, `<file2>`, ... | paths | Yes | Two or more `.fvc` files to correlate |

#### Behavior

- Aligns multiple flight logs by time
- Creates correlated output files
- Shows progress for each input file

#### Examples

```bash
# Correlate two flight logs
fvc df correlate flight1.fvc flight2.fvc

# Correlate multiple logs
fvc df correlate *.fvc

# Correlate with verbose output
fvc df correlate log1.fvc log2.fvc --verbose
```

---

### Command: fvc df help

Show help for a specific external format (including custom parameters).

#### Usage

```bash
fvc df help <format>
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<format>` | string | Yes | Format to show help for |

#### Examples

```bash
# Show help for NMEA format
fvc df help nmea

# Show help for SAFIR MQTT format
fvc df help safirmqtt
```

---

### Subcommands: fvc df flightlog

Flight log specific tools for analysis and manipulation.

#### Usage

```bash
fvc df flightlog <subcommand> [options]
```

#### Subcommands

| Subcommand | Description |
|------------|-------------|
| `stats` | Calculate statistics for a flight log |
| `split` | Split a flight log into daily files or by inactivity |
| `select` | Fetch a given element from the flight log |

---

#### Command: fvc df flightlog stats

Calculate statistics for a FVC data file.

##### Usage

```bash
fvc df flightlog stats <input_path> [options]
```

##### Options

```
--vdim <metric>          Vertical dimension metric (choices: alt, height, amsl), default: alt
--segment-by-height      Segment the log by height
--segment-height-meters <meters>  Height to segment by, default: 10.0
--segment-by-idle        Segment the log by idle time
--idle-time-seconds <seconds>  Idle time threshold, default: 60.0
--filter-by-duration     Filter the log by duration
--filter-duration-seconds <seconds>  Duration threshold, default: 300.0
--filter-displacement    Filter segments by spatial displacement
--displacement-lateral-meters <meters>  Lateral displacement threshold, default: 200.0
--displacement-vertical-meters <meters>  Vertical displacement threshold, default: 50.0
```

##### Examples

```bash
# Basic statistics
fvc df flightlog stats flight.fvc

# Statistics with height segmentation
fvc df flightlog stats flight.fvc --segment-by-height --segment-height-meters 15.0

# Statistics with idle time segmentation
fvc df flightlog stats flight.fvc --segment-by-idle --idle-time-seconds 120.0

# Statistics with displacement filtering
fvc df flightlog stats flight.fvc --filter-displacement --displacement-lateral-meters 300.0
```

---

#### Command: fvc df flightlog split

Split a flight log into daily files or by inactivity period.

##### Usage

```bash
fvc df flightlog split <input_path> [options]
```

##### Options

```
--mode <mode>                    Split mode (choices: day, inactivity), default: inactivity
--inactivity-threshold-seconds <seconds>  Inactivity threshold for inactivity mode, default: 300.0
--output-dir <directory>         Output directory (default: <input_path>/split)
```

##### Examples

```bash
# Split by inactivity (default)
fvc df flightlog split flight.fvc

# Split by day
fvc df flightlog split flight.fvc --mode day

# Split with custom inactivity threshold
fvc df flightlog split flight.fvc --inactivity-threshold-seconds 600.0

# Split with custom output directory
fvc df flightlog split flight.fvc --output-dir ./split_logs
```

---

#### Command: fvc df flightlog select

Fetch a given element from the flight log using Polars expression syntax.

##### Usage

```bash
fvc df flightlog select <input_path> <expression> [options]
```

##### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<expression>` | string | Yes | Polars expression to select data |

##### Options

```
--format <format>  Output format (choices: fvc, frames, ndjson), default: frames
```

##### Examples

```bash
# Select altitude column
fvc df flightlog select flight.fvc "col('alt')"

# Select multiple columns
fvc df flightlog select flight.fvc "col('lat'), col('lon'), col('alt')"

# Get JSON output
fvc df flightlog select flight.fvc "col('lat')" --json
```

---

### Subcommands: fvc df fusion

SAFIR Fusion data extraction tools.

#### Usage

```bash
fvc df fusion <subcommand> [options]
```

#### Subcommands

| Subcommand | Description |
|------------|-------------|
| `flightlog` | Extract fused flight log data from a replay file |

---

#### Command: fvc df fusion flightlog

Extract fused flight log data from a SAFIR Fusion replay file.

##### Usage

```bash
fvc df fusion flightlog --output-plots <plots_path> --output-tracks <tracks_path> <input_path>
```

##### Options

```
--output-plots <path>   Output file for plots (JSON Lines format)
--output-tracks <path>  Output file for tracks (JSON Lines format)
```

##### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<input_path>` | path | Yes | Path to the SAFIR Fusion replay file |

##### Examples

```bash
# Extract flight log data
fvc df fusion flightlog --output-plots plots.jl --output-tracks tracks.jl replay.jl
```

---

## Toolset: fvc calc (Geospatial Calculations)

The `fvc calc` toolset provides specialized geospatial calculations including epoch conversion, geoid undulation lookup, and terrain elevation queries.

### Global Options for fvc calc

```
--verbose, -v   Enable verbose output
--json          Make JSON default output format
--no-pprint     Disable colored pretty printing
--egm <path>    Custom EGM geoid data file (*.pgm)
```

### Commands

| Command | Description |
|---------|-------------|
| `epoch` | Convert UNIX timestamps to human-readable format |
| `undulation` | Get geoid undulation by latitude/longitude |
| `terrain` | Get terrain elevation by latitude/longitude |

---

### Command: fvc calc epoch

Convert UNIX timestamps to human-readable ISO format.

#### Usage

```bash
fvc calc epoch <timestamp> [options]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<timestamp>` | integer | Yes | UNIX timestamp (seconds or nanoseconds) |

#### Options

```
--nanoseconds   Use nanoseconds instead of milliseconds (default: milliseconds)
```

#### Examples

```bash
# Convert seconds timestamp
fvc calc epoch 1717020800
# Output: 2024-05-29T12:00:00+00:00

# Convert milliseconds timestamp
fvc calc epoch 1717020800000
# Output: 2024-05-29T12:00:00+00:00

# Convert nanoseconds timestamp
fvc calc epoch 1717020800000000000 --nanoseconds
# Output: 2024-05-29T12:00:00+00:00

# JSON output
fvc calc epoch 1717020800 --json
# Output: {"datetime": "2024-05-29T12:00:00+00:00"}
```

---

### Command: fvc calc undulation

Get geoid undulation (height above/below ellipsoid) by latitude and longitude using EGM geoid model.

#### Usage

```bash
fvc calc undulation <latitude> <longitude> [options]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<latitude>` | string | Yes | Latitude (e.g., "45.5" or "45°30'0"N) |
| `<longitude>` | string | Yes | Longitude (e.g., "-73.2" or "73°12'0"W) |

#### Options

```
--egm <path>    Custom EGM geoid data file (*.pgm)
```

#### Output

- Prints the geoid undulation value in meters
- In JSON mode, outputs: `{"undulation": <value>}`

#### Examples

```bash
# Get undulation for a location
fvc calc undulation "45.5" "-73.2"
# Output: 22.456

# Get undulation with custom EGM file
fvc calc undulation "45.5" "-73.2" --egm /path/to/custom.pgm

# JSON output
fvc calc undulation "45.5" "-73.2" --json
# Output: {"undulation": 22.456}
```

---

### Command: fvc calc terrain

Get terrain elevation (AMSL - Above Mean Sea Level) by latitude, longitude, and height.

#### Usage

```bash
fvc calc terrain <latitude> <longitude> <geo_amsl_height> [options]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<latitude>` | string | Yes | Latitude (e.g., "45.5" or "45°30'0"N) |
| `<longitude>` | string | Yes | Longitude (e.g., "-73.2" or "73°12'0"W) |
| `<geo_amsl_height>` | float | Yes | Height in meters (can be ellipsoid height or AMSL depending on --normal flag) |

#### Options

```
--normal              Use undulation instead of ellipsoid height (treat input as AMSL)
--copernicus-dir <path>  Directory containing Copernicus DEM files
--egm <path>         Custom EGM geoid data file (*.pgm)
```

#### Output

- Prints the terrain elevation in meters
- In JSON mode, outputs: `{"terrain": <value>}`

#### Examples

```bash
# Get terrain elevation (input is ellipsoid height)
fvc calc terrain "45.5" "-73.2" 100.5
# Output: 78.05

# Get terrain elevation with input as AMSL
fvc calc terrain "45.5" "-73.2" 100.5 --normal
# Output: 78.05

# Get terrain elevation with custom Copernicus DEM directory
fvc calc terrain "45.5" "-73.2" 100.5 --copernicus-dir /path/to/dem

# JSON output
fvc calc terrain "45.5" "-73.2" 100.5 --json
# Output: {"terrain": 78.05}
```

---

## Toolset: fvc render (Visualization Tools)

The `fvc render` toolset provides visualization capabilities for FVC data files, generating interactive maps showing flight paths.

### Global Options for fvc render

```
--verbose, -v   Enable verbose output
--json          Make JSON default output format
--no-pprint     Disable colored pretty printing
```

### Commands

| Command | Description |
|---------|-------------|
| `fl` | Generate map visualization for FVC data files |

---

### Command: fvc render fl

Generate an interactive map visualization for FVC data files (JSON Lines format).

#### Usage

```bash
fvc render fl <filename> [options]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<filename>` | path | Yes | Path to the `.fvc` file to visualize |

#### Options

```
--output, -o <path>  Output directory for generated files (default: ./results/render)
--title <title>      Title for the visualization (default: "FVC Data Visualization")
```

#### Behavior

- Reads FVC format files (JSON Lines)
- Creates an HTML visualization showing the flight path on an interactive map
- Generates files in the output directory:
  - `index.html` – Main visualization page
  - Map tiles and assets
- Automatically opens the visualization in your default web browser (if possible)

#### Examples

```bash
# Generate visualization with default settings
fvc render fl flight.fvc

# Generate visualization with custom output directory
fvc render fl flight.fvc --output ./my_visualization

# Generate visualization with custom title
fvc render fl flight.fvc --title "My Flight Path"

# Generate visualization with verbose output
fvc render fl flight.fvc --verbose
```

---

## Shell Integration

fvctools provides shell integration utilities for PowerShell.

### Command: fvc shell pwsh

Generate a PowerShell integration script that allows using `fvc` commands with PowerShell JSON parsing.

#### Usage

```bash
fvc shell pwsh
```

#### Output

```powershell
function FvcTool {
    return $(fvc --json --no-pprint @args) | ConvertFrom-Json
}
```

#### Usage in PowerShell

```powershell
# Save the output to your PowerShell profile
fvc shell pwsh >> $PROFILE

# Then use it like:
$result = FvcTool df validate flight.fvc
```

---

## Command Summary

| Toolset | Commands | Description |
|---------|----------|-------------|
| **fvc** | Global options | Version, help, verbose, JSON output, AWS profile, EGM geoid |
| **fvc df** | convert, export, validate, correlate, help, flightlog, fusion | Data file conversion, validation, correlation, and manipulation |
| **fvc calc** | epoch, undulation, terrain | Geospatial calculations and conversions |
| **fvc render** | fl | Flight log visualization |
| **fvc shell** | pwsh | PowerShell integration |

---

## Tips and Best Practices

### Input File Specification

Most commands accept input files in two ways:

```bash
# Using --in option
fvc df --in input.nmea convert nmea output.fvc

# Using positional argument (first argument after command)
fvc df input.nmea convert nmea output.fvc
```

### Output File Specification

- For `convert`: Output path is optional; if omitted, inferred from input path with `.fvc` extension
- For `export`: Output path is optional; format-specific behavior
- For `validate`: No output file needed
- For `correlate`: Output files are generated automatically

### JSON Output

Use `--json` flag to get machine-readable JSON output:

```bash
fvc calc undulation "45.5" "-73.2" --json
fvc df validate flight.fvc --json
```

### Verbose Mode

Use `-v` or `--verbose` to see detailed progress and debugging information:

```bash
fvc df --in large_file.nmea convert nmea output.fvc --verbose
```

### Custom EGM Geoid

For high-precision calculations, you can specify a custom EGM geoid file:

```bash
fvc calc terrain "45.5" "-73.2" 100.5 --egm /path/to/custom.pgm
fvc df --egm /path/to/custom.pgm convert nmea output.fvc
```

### Cache Directory

Set the `FVC_CACHE` environment variable to specify a default cache directory for external data:

```bash
export FVC_CACHE=/path/to/cache
fvc df --cache-dir /path/to/cache convert nmea output.fvc
```

---

## Error Handling

Common error scenarios and solutions:

### Input/Output Path Conflict

```
Error: Input and output paths are the same
```

**Solution**: Specify different input and output paths.

```bash
fvc df input.fvc convert nmea output.fvc
```

### Missing Input File

```
Error: Path 'missing.nmea' does not exist
```

**Solution**: Verify the input file exists and the path is correct.

### Invalid Format

```
Error: Invalid value for '<format>': ...
```

**Solution**: Check available formats with `fvc df --help` and use a supported format.

### Validation Failure

```
Validation failed
```

**Solution**: The file does not conform to the FVC schema. Check the file integrity.

### Missing Dependencies

For `fvc calc terrain`, ensure Copernicus DEM files are available if not using `--copernicus-dir`.

---

## See Also

- [Data Formats Reference](/openwiki/architecture/data-formats.md) – Detailed information about FVC file format
- [Workflows: Conversion](/openwiki/workflows/conversion.md) – Common conversion workflows
- [Workflows: Validation](/openwiki/workflows/validation.md) – Data validation best practices
