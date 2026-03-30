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
