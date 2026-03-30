# Design Spec: fvctools README Overhaul

**Status**: Draft
**Owner**: Gemini CLI
**Date**: 2026-03-30

## 1. Goal
Replace the current minimal `README.md` with a comprehensive, professional, and modular-feeling single-file guide that explains the purpose, installation, and usage of the entire `fvctools` suite.

## 2. Structure & Sections

### 2.1 Project Overview
- **Name**: Flyvercity CLI Tools Suite (`fvctools`).
- **Purpose**: Modular CLI for aviation-related geospatial data processing (Flight Logs, Radar Logs, etc.).
- **Tech**: Python 3.12, Polars, Click, JSON-Lines format.

### 2.2 Installation & Integration
- **Direct Usage (Python)**: `uv sync`, `uv run fvc`.
- **PowerShell (Windows)**:
    - Installation: `.\scripts\Install-FvcTools.ps1`.
    - Loading: `. .\pwsh\Load-FvcTools.ps1`.
    - Usage as an object: `(FvcTool <args>)`.

### 2.3 Core Toolsets (Usage Guide)
- **`fvc df` (Data File)**: 
    - `convert`: Transform external logs (NMEA, ULog, DJI, etc.) to `.fvc`.
    - `validate`: Check `.fvc` files against the Flyvercity JSON Schema.
    - `correlate`: Link flight data with external events.
- **`fvc calc` (Calculations)**:
    - `undulation`: Geoid height (EGM96).
    - `terrain`: Terrain altitude (DEM).
- **`fvc render` (Visualization)**:
    - `fl`: Generate interactive HTML maps.

### 2.4 The Flyvercity Data Format (.fvc)
- Explanation of JSON-Lines.
- **Metadata**: The required first line.
- **Data**: Subsequent `FLIGHTLOG` or `RADARLOG` records.

### 2.5 Supported Formats Table
A simple Markdown table listing all modules in `src/fvc/tools/df/xformats/`.

### 2.6 Development & Contributing
- Project structure overview.
- Adding a new `xformat`.
- Testing: `uv run pytest`.
- Linting: `uv run ruff check .`.

## 3. Implementation Details
- **Markdown Style**: GitHub-Flavored.
- **Code Blocks**: Always include language identifiers (`bash`, `pwsh`, `json`).
- **Auto-Discovery**: I will list the `xformats` directory to generate the table.

## 4. Verification
- All paths mentioned in the README must exist.
- All CLI commands must have valid `--help` descriptions in the source.
- Markdown must render correctly on standard viewers.
