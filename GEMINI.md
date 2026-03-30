# Flyvercity CLI Tools Suite (fvctools)

## Project Overview
`fvctools` is a comprehensive Python CLI suite for processing, converting, and validating geospatial data, specifically flight logs and radar logs. It serves as the primary toolset for Flyvercity's data pipeline, enabling conversion from various external formats (e.g., NMEA, DJI Datcon, PX4 ULog, Robin Radar) into a unified, schema-validated JSON-Lines format (`.fvc`).

### Core Technologies
- **Language:** Python 3.12+
- **CLI Framework:** [Click](https://click.palletsprojects.com/)
- **Data Processing:** [Polars](https://pola.rs/), [GeoPandas](https://geopandas.org/), [SciPy](https://scipy.org/)
- **Validation:** [jsonschema](https://python-jsonschema.readthedocs.io/)
- **Dependency Management:** [uv](https://github.com/astral-sh/uv)
- **Build System:** [hatchling](https://hatch.pypa.io/)
- **UI/Logging:** [Rich](https://rich.readthedocs.io/)

### Architecture
- `src/fvc/tools/cli.py`: Main entry point.
- `src/fvc/tools/df/`: Data File tools (conversion, validation, correlation).
- `src/fvc/tools/df/xformats/`: Handlers for external data formats.
- `src/fvc/tools/calc/`: Geospatial calculations (geoid, terrain).
- `src/fvc/tools/render/`: HTML/JS report generation using Jinja2 templates.
- `src/fvc/tools/df/schema.yaml`: Central source of truth for the `.fvc` data format.

## Building and Running

### Prerequisites
- Install `uv`: `pip install uv`
- Python 3.12+

### Development Commands
- **Install dependencies:** `uv sync`
- **Run CLI:** `uv run fvc [args]`
- **Run Tests:** `uv run pytest`
- **Linting:** `uv run ruff check .`
- **Formatting:** `uv run ruff format .`

### Key CLI Usage
- **Convert format:** `fvc df convert <x_format> <input_file>`
- **Validate FVC file:** `fvc df validate <fvc_file>`
- **Render report:** `fvc render <fvc_file>`
- **Calc undulation:** `fvc calc undulation <lat> <lon>`

## Development Conventions

### Data Format (.fvc)
- Files are JSON-Lines (`.jsonl`).
- The **first line** is a `METADATA` record containing `content`, `source`, `origin`, and optional `polar_sensor` info.
- Subsequent lines are data records (e.g., `FLIGHTLOG`, `RADARLOG`) validated against the schemas in `src/fvc/tools/df/schema.yaml`.

### Adding a New Format
1. Create a new module in `src/fvc/tools/df/xformats/`.
2. Implement `convert_to_fvc(params, meta, input_path, io)`.
3. Optionally implement `export_from_fvc(params, output_path)`.
4. Register the format name in the `convert_command` docstring in `src/fvc/tools/df/cli.py`.

### Code Style
- Follow `ruff` configuration (line-length 120, single quotes for formatting).
- Use `benedict` for dictionary manipulation.
- Prefer `rich` for console output and progress bars.

### Testing
- Add tests to the `tests/` directory.
- Use `pytest`.
- Mock external services (like S3) using `boto3` session mocking if necessary.
