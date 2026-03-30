# Flyvercity CLI Tools Suite (fvctools)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`fvctools` is a modular Python-based CLI suite designed for the processing, conversion, and validation of geospatial aviation data, including Flight Logs and Radar Logs. It serves as the backbone of Flyvercity's data pipeline, enabling seamless data integration and analysis across different platforms and formats.

## Installation

### Unix Shells (Linux, macOS, WSL)

```bash
source scripts/Login-ToCodeArtifact.sh
./scripts/Install-FvcTools.sh
```

### PowerShell

```pwsh
.\scripts\Login-ToCodeArtifact.ps1
.\scripts\Install-FvcTools.ps1
```

## Core Toolsets

The `fvctools` suite is organized into specialized toolsets for data manipulation, geospatial calculations, and visualization.

### Data File Tools (`fvc df`)

The `df` toolset manages the conversion, validation, and correlation of aviation data files into the unified Flyvercity (`.fvc`) format.

- **Conversion**: Converts external formats (NMEA, ULog, DJI, etc.) to `.fvc`.
  ```bash
  uv run fvc df --in flight.nmea convert nmea flight.fvc
  ```
- **Validation**: Verifies that an `.fvc` file complies with the project's data schema.
  ```bash
  uv run fvc df --in flight.fvc validate
  ```
- **Correlation**: Synchronizes and merges multiple flight or radar log files.
  ```bash
  uv run fvc df correlate log1.fvc log2.fvc
  ```

### Geospatial Calculations (`fvc calc`)

Provides utilities for precise coordinate and altitude calculations.

- **Undulation**: Retrieves the EGM96 geoid undulation for a given latitude and longitude.
  ```bash
  uv run fvc calc undulation 52.3 4.9
  ```
- **Terrain**: Performs terrain elevation lookups using Digital Elevation Models (DEM).
  ```bash
  uv run fvc calc terrain 52.3 4.9 100.0
  ```

### Visualization (`fvc render`)

Generates interactive visualizations for flight data analysis.

- **Interactive Maps (`fl`)**: Creates a standalone HTML visualization of flight paths.
  ```bash
  uv run fvc render fl flight.fvc --output ./map_results
  ```

## The Flyvercity Data Format (.fvc)

The `.fvc` format is the unified data standard used by all Flyvercity tools. It is a [JSON-Lines](https://jsonlines.org/) (`.jsonl`) formatted file where each line is a valid JSON object.

### Structure

1.  **Metadata Line**: The **first line** of every `.fvc` file must be a `METADATA` record. It contains essential information about the file's content and its origin.
    - `content`: The type of data contained (e.g., `flightlog`, `radarlog`).
    - `source`: The original format the data was converted from.
    - `origin`: The name of the original source file or system.
2.  **Data Records**: Subsequent lines contain individual data records (e.g., `FLIGHTLOG` or `RADARLOG` entries) that follow the schemas defined in the project.

### Example

```json
{"content": "flightlog", "source": "nmea", "origin": "flight_data_20231201.log"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}}
```

## Supported External Formats

Flyvercity CLI tools can convert data from a variety of external aviation and geospatial formats into the unified `.fvc` format.

| Format Name | Description | Source Module |
| :--- | :--- | :--- |
| **AgentFly** | AgentFly simulator logs | `agentfly` |
| **ART** | ART log format | `artlog` |
| **Courageous** | Courageous project logs | `courageous` |
| **CS Group** | CS Group logs | `csgroup` |
| **DJI Datcon** | DJI Datcon logs | `datcon` |
| **GeoJSON** | GeoJSON format | `geojson` |
| **Gnettrack** | Gnettrack logs | `gnettrack` |
| **Manna** | Manna drone logs | `manna` |
| **NMEA** | NMEA GPS logs | `nmea` |
| **Robin Radar** | Robin Radar XML | `robinradar` |
| **Safir MQTT** | Safir MQTT logs | `safirmqtt` |
| **Senhive** | Senhive logs | `senhive` |
| **PX4 ULog** | PX4 ULog logs | `ulog` |

### PowerShell Helper (`fvc shell`)

For Windows-based workflows, `fvctools` provides a PowerShell integration that treats CLI outputs as first-class objects, enabling advanced automation and scripting.

1.  **Enable Integration**:
    ```pwsh
    Invoke-Expression (fvc shell pwsh)
    ```
2.  **Object-Oriented Usage**:
    Outputs are automatically parsed into PowerShell objects for easy property access:
    ```pwsh
    # Access the undulation value directly from the command output
    $height = (FvcTool calc undulation 52.3 4.9).undulation
    ```

## Development

We welcome contributions to `fvctools`! Follow these guidelines to get started.

### Adding a New Format

To add support for a new data format, create a new module in `src/fvc/tools/df/xformats/`.

#### Required Implementation

Each format module must implement the `convert_to_fvc` function:

```python
def convert_to_fvc(params, metadata, input_path, output):
    """
    Args:
        params (dict): CLI parameters and custom options.
        metadata (dict): Metadata to be written as the first line.
        input_path (Path): Path to the source file.
        output (JsonlinesIO): Unified IO handler for writing .fvc records.
    """
    # Implementation here
    ...
```

### Testing

Tests are located in the `tests/` directory. Use `pytest` to run the suite:

```bash
uv run pytest
```

### Linting & Formatting

We use `ruff` to ensure code quality and consistent formatting.

- **Check**:
  ```bash
  uv run ruff check .
  ```
- **Format**:
  ```bash
  uv run ruff format .
  ```

## For Developers

The project uses [uv](https://github.com/astral-sh/uv) for dependency management and environment isolation.

1.  **Install dependencies**:
    ```bash
    uv sync
    ```
2.  **Verify installation**:
    ```bash
    uv run fvc --help
    ```

### For Windows/PowerShell Users

A specialized installation script is provided for Windows environments to set up the CLI tools locally.

1.  **Install**:
    Run the provided installation script:
    ```pwsh
    .\scripts\Install-FvcTools.ps1
    ```
2.  **Load into session**:
    To load the tools into your current PowerShell session, source the loader script:
    ```pwsh
    . .\pwsh\Load-FvcTools.ps1
    ```

### For Linux/macOS Users (Bash)

Equivalent Bash scripts are provided for Linux and macOS environments.

1.  **Authenticate**:
    Fetch the CodeArtifact token and set environment variables:
    ```bash
    source scripts/Login-ToCodeArtifact.sh
    ```
2.  **Install**:
    Run the installation script:
    ```bash
    ./scripts/Install-FvcTools.sh
    ```