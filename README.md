# Flyvercity CLI Tools Suite (fvctools)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`fvctools` is a modular Python-based CLI suite designed for the processing, conversion, and validation of geospatial aviation data, including Flight Logs and Radar Logs. It serves as the backbone of Flyvercity's data pipeline, enabling seamless data integration and analysis across different platforms and formats.

## Installation

### For Developers

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
