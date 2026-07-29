---
type: Quickstart
title: fvctools Quickstart
description: Entry point for Flyvercity CLI Tools Suite documentation with overview and navigation
---

# Flyvercity CLI Tools Suite (fvctools)

Welcome to the OpenWiki documentation for fvctools, a modular Python-based CLI suite for processing, converting, and validating geospatial aviation data.

## Overview

`fvctools` is the backbone of Flyvercity's data pipeline, enabling seamless data integration and analysis across different platforms and formats. The suite is organized into specialized toolsets for data manipulation, geospatial calculations, and visualization.

## Key Concepts

### Core Toolsets

- **Data File Tools (`fvc df`)**: Manages conversion, validation, and correlation of aviation data files
- **Geospatial Calculations (`fvc calc`)**: Provides utilities for coordinate and altitude calculations  
- **Visualization (`fvc render`)**: Generates interactive visualizations for flight data analysis
- **PowerShell Integration (`fvc shell`)**: Windows-based workflow automation

### The Flyvercity Data Format (.fvc)

The unified `.fvc` format is a JSON-Lines formatted file used by all Flyvercity tools. Each file contains:
- A metadata line with content type, source, and origin information
- Data records following project schemas

## Getting Started

### Installation

See the [Setup Guide](operations/setup.md) for detailed installation instructions.

### Basic Usage

```bash
# Convert a file to FVC format
uv run fvc df --in flight.nmea convert nmea flight.fvc

# Validate an FVC file
uv run fvc df --in flight.fvc validate

# Calculate geoid undulation
uv run fvc calc undulation 52.3 4.9
```

## Documentation Sections

### Architecture
- [Overview](architecture/overview.md): High-level system architecture
- [Data Formats](architecture/data-formats.md): FVC format structure and design
- [Tools Architecture](architecture/tools.md): Tool organization and implementation

### Workflows
- [Data Conversion](workflows/conversion.md): Conversion processes and optimizations
- [Data Validation](workflows/validation.md): Validation workflows

### Domain Knowledge
- [Supported Formats](domain/formats.md): All supported external data formats

### Operations
- [Setup and Installation](operations/setup.md): Environment setup and dependencies
- [Development Workflow](operations/development.md): Development practices and tooling

### Testing
- [Testing Approach](testing/overview.md): Testing strategy and implementation

### Integrations
- [Polars Integration](integrations/polars.md): Polars optimization and usage patterns

## Recent Updates

The project has recently undergone significant optimizations:
- **Polars Integration**: Several data format converters have been optimized using Polars for better performance
- **Dependency Management**: Reorganized pyproject.toml structure and removed flake8

## Backlog

No backlogged documentation areas at this time.