---
type: DataFormatArchitecture
title: Data Format Architecture
description: Architecture and design of the Flyvercity FVC data format
---

# Data Format Architecture

The Flyvercity Data Format (`.fvc`) is the unified data standard that enables interoperability across all tools in the suite.

## Format Specification

### Structure

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
classDiagram
    class FVCFile {
        +METADATA record (first line)
        +DATA records (subsequent lines)
    }
    
    class METADATA {
        +content: string
        +source: string  
        +origin: string
    }
    
    class DATA_RECORD {
        <<abstract>>
    }
    
    class FLIGHTLOG {
        +time: object
        +pos: object
        +...other flight data
    }
    
    class RADARLOG {
        +time: object
        +position: object
        +...other radar data
    }
    
    FVCFile --> METADATA
    FVCFile --> DATA_RECORD
    DATA_RECORD <|-- FLIGHTLOG
    DATA_RECORD <|-- RADARLOG
```

### Technical Details

- **Format**: JSON-Lines (`.jsonl`) where each line is a valid JSON object
- **First Line**: Must be a METADATA record containing:
  - `content`: Type of data (e.g., `flightlog`, `radarlog`)
  - `source`: Original format the data was converted from
  - `origin`: Name of the original source file or system
- **Subsequent Lines**: Individual data records following project schemas

### Example

```json
{"content": "flightlog", "source": "nmea", "origin": "flight_data_20231201.log"}
{"time": {"unix": 1756033206882}, "pos": {"loc": {"lat": 52.3, "lon": 4.9, "alt": 100.5}}}
```

## Schema Management

### Schema Files

- **Location**: `src/fvc/tools/df/schema.yaml`
- **Validation**: Uses JSONSchema for structure validation
- **Documentation**: Schema documentation in `docs/schema/`

### Schema Types

1. **METADATA**: File metadata and provenance
2. **FLIGHTLOG**: Flight data records with time, position, and flight parameters
3. **RADARLOG**: Radar data records with time, position, and radar-specific data
4. **CORRELATION**: Correlation results between multiple data sources

## Design Rationale

### Why JSON-Lines?

- **Streaming Friendly**: Easy to process large files line by line
- **Human Readable**: JSON format is easily inspectable
- **Tool Compatible**: Works well with standard Unix tools and data processing libraries
- **Schema Flexible**: Can evolve with additional record types

### Why Unified Format?

- **Consistency**: All tools work with the same data structure
- **Interoperability**: Data can flow between different processing stages
- **Validation**: Single validation framework for all data
- **Extensibility**: New tools can be added without format changes

## Relationships

- **Supported Formats**: The FVC format is used to unify all [supported external formats](domain/formats.md)
- **Conversion Workflows**: Format converters transform external data to FVC in the [conversion workflows](workflows/conversion.md)
- **Validation**: The format is validated by tools described in [validation workflows](workflows/validation.md)

## Source References

- Schema Definition: `src/fvc/tools/df/schema.yaml`
- Schema Code: `src/fvc/tools/df/schema.py`
- Validation Engine: `src/fvc/tools/df/core.py`
- Format Documentation: `docs/schema/README.md`