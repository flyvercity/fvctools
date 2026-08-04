---
type: Setup Guide
title: Development and Production Setup

description: Complete guide to setting up fvctools for development and production use, including dependencies, environment configuration, and installation
resource: /pyproject.toml

tags: [setup, installation, development, production, dependencies]
---

# Development and Production Setup

This guide provides complete instructions for setting up **fvctools** for both **development** and **production** environments.

## Overview

fvctools requires careful setup of:

- **Python environment** (Python 3.12+)
- **Dependencies** (via uv/pip)
- **Development tools** (linters, formatters, test runners)
- **Environment configuration** (environment variables, config files)
- **CodeArtifact access** (for private package dependencies)

## Prerequisites

### 1. Python 3.12+

fvctools requires **Python 3.12 or later**:

```bash
# Check Python version
python --version
# or
python3 --version

# Should output: Python 3.12.x or higher
```

**Install Python if needed**:

- **Linux/macOS**: Use pyenv or system package manager
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Recommended**: Python 3.12.0 or later

### 2. UV Package Manager

fvctools uses **uv** for package management (faster than pip):

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

**Alternative**: Use pip (slower but works):

```bash
pip install --upgrade pip
```

### 3. Git

Required for version control and cloning:

```bash
# Check Git installation
 git --version

# Should output: git version 2.x.x or higher

# Install Git if needed
# Linux: sudo apt-get install git
# macOS: brew install git
# Windows: Download from git-scm.com
```

### 4. Node.js (for OpenWiki)

Required for OpenWiki documentation generation:

```bash
# Check Node.js installation
node --version
npm --version

# Should output: v22.x.x or higher

# Install Node.js if needed
# Linux/macOS: Use nvm or system package manager
# Windows: Download from nodejs.org
```

## Installation Methods

### Method 1: Development Installation (Editable)

For development work, install in **editable mode**:

```bash
# Clone the repository (if not already cloned)
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Install in development mode
uv pip install -e ".[dev]"

# Verify installation
fvc --version
```

**What this does**:
- Installs fvctools in editable mode (changes to source code are immediately available)
- Installs development dependencies (pytest, ruff, etc.)
- Creates symlinks so `fvc` command works globally

### Method 2: Production Installation

For production use, install normally:

```bash
# Install from local directory
uv pip install .

# Or install from Git repository
uv pip install git+https://github.com/flyvercity/fvctools.git

# Verify installation
fvc --version
```

**What this does**:
- Installs fvctools in regular mode
- Only production dependencies are installed
- No development tools

### Method 3: Using Install Scripts

fvctools provides installation scripts:

```bash
# Unix Shells (Linux, macOS, WSL)
source scripts/Login-ToCodeArtifact.sh
./scripts/Install-FvcTools.sh

# PowerShell (Windows)
."scripts\Login-ToCodeArtifact.ps1"
."scripts\Install-FvcTools.ps1"
```

**What these scripts do**:
1. Authenticate with AWS CodeArtifact
2. Install fvctools with all dependencies
3. Set up environment variables

## Environment Configuration

### 1. Environment Variables

fvctools uses environment variables for configuration:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FVC_DATA_DIR` | Default data directory | No | `./data` |
| `FVC_LOG_LEVEL` | Logging level | No | `INFO` |
| `FVC_VALIDATE_STRICT` | Enable strict validation | No | `false` |
| `AWS_REGION` | AWS region for CodeArtifact | Yes (for CodeArtifact) | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes (for CodeArtifact) | None |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes (for CodeArtifact) | None |

**Example**:

```bash
# Set environment variables
export FVC_DATA_DIR="/data/fvctools"
export FVC_LOG_LEVEL="DEBUG"
export AWS_REGION="us-west-2"

# Or use a .env file (create .env in project root)
cat > .env << EOF
FVC_DATA_DIR="/data/fvctools"
FVC_LOG_LEVEL="DEBUG"
AWS_REGION="us-west-2"
EOF
```

**Note**: `.env` files are not committed to git (see `.gitignore`)

### 2. AWS CodeArtifact Configuration

For private package dependencies:

```bash
# Configure AWS credentials
aws configure

# Set AWS region
export AWS_REGION="us-east-1"

# Login to CodeArtifact
source scripts/Login-ToCodeArtifact.sh

# Or in PowerShell
."scripts\Login-ToCodeArtifact.ps1"
```

**Required IAM permissions**:
- `codeartifact:GetAuthorizationToken`
- `codeartifact:ReadFromRepository`

## Development Environment Setup

### 1. Clone the Repository

```bash
# Clone repository
git clone https://github.com/flyvercity/fvctools.git
cd fvctools

# Or if already cloned
cd fvctools
```

### 2. Install Development Dependencies

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Or install dev dependencies separately
uv pip install duct jsonschema2md ptpython pytest ruff
```

### 3. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

**What this does**:
- Installs git pre-commit hooks
- Runs linters and formatters before commits
- Ensures code quality

### 4. Verify Installation

```bash
# Check fvc command
fvc --version

# Check Python package
python -c "import fvc; print(fvc.__version__)"

# List installed packages
uv pip list | grep fvc
```

## Production Environment Setup

### 1. Install Production Dependencies

```bash
# Install only production dependencies
uv pip install .

# Or with uv
uv sync --frozen
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install in virtual environment
uv pip install .
```

### 3. Configure Production Environment

```bash
# Set production environment variables
export FVC_LOG_LEVEL="INFO"
export FVC_DATA_DIR="/var/lib/fvctools"

# Create data directory
mkdir -p "$FVC_DATA_DIR"
chmod 755 "$FVC_DATA_DIR"
```

### 4. Test Production Installation

```bash
# Test fvc command
fvc --version

# Test conversion
fvc df --in test.nmea convert nmea test.fvc

# Test validation
fvc df --in test.fvc validate
```

## Dependency Management

### 1. Adding New Dependencies

```bash
# Add production dependency
uv pip install new-package
uv pip compile pyproject.toml --output pyproject.toml

# Add development dependency
declare -g new-dev-package
uv pip install new-dev-package
uv pip compile pyproject.toml --output pyproject.toml

# Update uv.lock
uv sync
```

### 2. Updating Dependencies

```bash
# Update all dependencies
uv pip compile --upgrade pyproject.toml --output pyproject.toml
uv sync

# Update specific dependency
uv pip install --upgrade package-name
uv pip compile --upgrade pyproject.toml --output pyproject.toml
uv sync
```

### 3. Removing Dependencies

```bash
# Remove dependency
uv pip uninstall package-name
uv pip compile pyproject.toml --output pyproject.toml
uv sync
```

### 4. Dependency Groups

fvctools uses dependency groups:

```toml
[project]
dependencies = [
    "polars>=1.35.1",
    "pygeodesy>=24.11.11",
    # ... other dependencies
]

[dependency-groups]
dev = [
    "duct>=1.0.1",
    "jsonschema2md>=1.7.0",
    "ptpython>=3.0.30",
    "pytest>=9.0.2",
    "ruff>=0.14.0",
]
```

**Install dev group**:
```bash
uv pip install -e ".[dev]"
```

## Development Workflow

### 1. Code Structure

```
fvctools/
├── src/fvc/              # Main source code
│   ├── __init__.py
│   ├── tools/
│   │   ├── cli.py        # CLI entry point
│   │   ├── df/
│   │   ├── calc/
│   │   └── render/
├── tests/               # Test files
├── scripts/             # Utility scripts
├── pyproject.toml       # Project configuration
└── .pre-commit-config.yaml  # Pre-commit hooks
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_nmea_xformat.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/fvc --cov-report=html

# Run specific test
pytest -k "test_nmea_conversion"
```

### 3. Code Formatting

```bash
# Format with ruff
ruff format src/fvc

# Lint with ruff
ruff check src/fvc

# Check types with mypy (if configured)
mypy src/fvc
```

### 4. Running the CLI

```bash
# Test fvc command
fvc --version
fvc --help

# Test df toolset
fvc df --help

# Test conversion
fvc df --in test.nmea convert nmea test.fvc

# Test validation
fvc df --in test.fvc validate
```

### 5. Debugging

```bash
# Debug with ptpython
ptpython

# Debug with pdb
python -m pdb -m fvc.tools.cli

# Run with logging
FVC_LOG_LEVEL=DEBUG fvc df --in test.fvc validate
```

## Production Deployment

### 1. Deployment Options

| Option | Description | Recommended |
|--------|-------------|-------------|
| **Local installation** | Install on local machine | Development |
| **Virtual environment** | Isolated Python environment | Production |
| **Docker container** | Containerized deployment | Production |
| **System-wide** | System Python installation | Development only |

### 2. Docker Deployment

Example Dockerfile:

```dockerfile
# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir uv
RUN uv pip install --no-cache-dir .

# Set environment variables
ENV FVC_DATA_DIR=/data
ENV FVC_LOG_LEVEL=INFO

# Create data directory
RUN mkdir -p /data && chown -R 1000:1000 /data

# Set user
USER 1000

# Command to run
CMD ["fvc", "--version"]
```

**Build and run**:

```bash
# Build image
docker build -t fvctools .

# Run container
docker run -it fvctools

# Run with volume for data
docker run -it -v /data:/data fvctools
```

### 3. Systemd Service (Linux)

Example systemd service file:

```ini
# /etc/systemd/system/fvctools.service

[Unit]
Description=Flyvercity CLI Tools Service
After=network.target

[Service]
Type=simple
User=fvctools
Group=fvctools
WorkingDirectory=/opt/fvctools
Environment="FVC_DATA_DIR=/var/lib/fvctools"
Environment="FVC_LOG_LEVEL=INFO"
ExecStart=/opt/fvctools/.venv/bin/fvc --version
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Setup**:

```bash
# Create user
sudo useradd -r -s /bin/false fvctools

# Create directories
sudo mkdir -p /opt/fvctools /var/lib/fvctools
sudo chown fvctools:fvctools /opt/fvctools /var/lib/fvctools

# Install fvctools
sudo -u fvctools bash -c "cd /opt/fvctools && uv pip install ."

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fvctools
sudo systemctl start fvctools

# Check status
sudo systemctl status fvctools
```

### 4. Cron Jobs (Scheduled Tasks)

Example cron job for batch processing:

```bash
# Edit crontab
crontab -e

# Add job (runs daily at 2 AM)
0 2 * * * /opt/fvctools/.venv/bin/fvc df --in /data/input/*.nmea convert nmea /data/output/{}.fvc

# Or use a script
0 2 * * * /opt/fvctools/scripts/batch_convert.sh
```

## Troubleshooting Setup Issues

### 1. Python Version Issues

**Error**: Wrong Python version

**Solutions**:

```bash
# Check Python version
python --version

# Use pyenv to manage Python versions
pyenv install 3.12.0
pyenv global 3.12.0

# Or use uv to run with specific Python
uv run --python 3.12 python -m fvc.tools.cli
```

### 2. Dependency Installation Issues

**Error**: Cannot install dependencies

**Solutions**:

```bash
# Check uv/pip version
uv --version
pip --version

# Upgrade uv/pip
uv pip install --upgrade uv pip

# Try installing with --no-deps
uv pip install --no-deps .

# Check network connectivity
ping pypi.org

# Check AWS CodeArtifact access
aws codeartifact get-authorization-token --domain my-domain
```

### 3. CodeArtifact Authentication Issues

**Error**: Cannot access private packages

**Solutions**:

```bash
# Re-authenticate
source scripts/Login-ToCodeArtifact.sh

# Check AWS credentials
aws sts get-caller-identity

# Check CodeArtifact permissions
aws codeartifact list-repositories --domain my-domain
```

### 4. Permission Issues

**Error**: Permission denied

**Solutions**:

```bash
# Check file permissions
ls -la

# Fix permissions
chmod +x scripts/*.sh
chmod +x scripts/*.ps1

# Use virtual environment
python -m venv .venv
source .venv/bin/activate

# Run as specific user
sudo -u fvctools command
```

### 5. Missing System Dependencies

**Error**: System libraries missing

**Solutions**:

```bash
# Linux (Ubuntu/Debian)
sudo apt-get install -y python3-dev build-essential

# macOS (Homebrew)
brew install python

# Windows
# Install Visual C++ Build Tools
```

## Environment Management

### 1. Virtual Environments

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Deactivate
deactivate

# Delete
rm -rf .venv
```

### 2. Environment Variables Management

```bash
# Set temporary variable
export VAR_NAME=value

# Set permanent variable (Linux/macOS)
echo 'export VAR_NAME=value' >> ~/.bashrc
echo 'export VAR_NAME=value' >> ~/.zshrc
source ~/.bashrc

# Set permanent variable (Windows)
# System Properties → Environment Variables

# Use .env file (development only)
cat > .env << EOF
VAR1=value1
VAR2=value2
EOF
```

### 3. Dependency Isolation

```bash
# Use uv for dependency management
uv pip install package-name

# Use virtual environments per project
python -m venv .venv
source .venv/bin/activate

# Use uv.lock for reproducible builds
uv sync --frozen
```

## Security Considerations

### 1. Credential Management

**Never commit credentials**:

```bash
# Bad: Commit .env file
git add .env
git commit -m "Add config"

# Good: Add to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Ignore .env files"
```

### 2. AWS Credentials

```bash
# Use AWS credentials file
~/.aws/credentials

# Or environment variables
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

# Or IAM roles (for EC2, ECS, etc.)
```

### 3. CodeArtifact Access

```bash
# Use temporary credentials
source scripts/Login-ToCodeArtifact.sh

# Tokens expire (typically 12 hours)
# Re-authenticate as needed
```

### 4. File Permissions

```bash
# Set appropriate permissions
chmod 600 .env  # Only owner can read
chmod 700 scripts/  # Only owner can execute

# Run as non-root user when possible
sudo -u fvctools command
```

## Performance Optimization

### 1. Memory Usage

```bash
# Monitor memory usage
/top
/htop

# Use lazy evaluation with Polars
lazy_df = df.lazy()
result = lazy_df.filter(...).collect()

# Process in chunks for large files
chunk_size = 10000
for chunk in df.iter_slices(chunk_size):
    process_chunk(chunk)
```

### 2. CPU Usage

```bash
# Monitor CPU usage
/top
/htop

# Use parallel processing
find ./input -name "*.nmea" | parallel -j $(nproc) process_file {}

# Use Polars parallel operations
# Polars automatically parallelizes operations
```

### 3. Disk I/O

```bash
# Monitor disk usage
/df -h

# Use efficient file formats
# JSON-Lines (.jsonl) for streaming
# Parquet for columnar storage

# Compress large files
gzip large_file.fvc
```

## Monitoring and Logging

### 1. Logging Configuration

```bash
# Set log level
export FVC_LOG_LEVEL=DEBUG

# Log to file
fvc df --in file.fvc validate 2>&1 | tee validation.log

# Structured logging (if configured)
python -m fvc.tools.cli --log-format json
```

### 2. Monitoring Tools

```bash
# Check system resources
/top
/htop
/df -h

# Check Python processes
/ps aux | grep python

# Check disk space
/du -sh /var/lib/fvctools
```

## Backup and Recovery

### 1. Backup Strategy

```bash
# Backup data directory
rsync -av /var/lib/fvctools/ /backup/fvctools/$(date +%Y%m%d)/

# Backup configuration
cp /etc/systemd/system/fvctools.service /backup/fvctools/config/

# Version control for scripts
cp scripts/*.sh /backup/fvctools/scripts/
```

### 2. Recovery Plan

```bash
# Restore from backup
rsync -av /backup/fvctools/latest/ /var/lib/fvctools/

# Reinstall fvctools
cd /opt/fvctools
git pull
git checkout <version>
uv pip install .

# Restart service
sudo systemctl restart fvctools
```

## Upgrading fvctools

### 1. Upgrade Process

```bash
# Update from git
cd fvctools
git pull

# Upgrade dependencies
uv pip install --upgrade .

# Test upgrade
fvc --version
pytest

# Deploy upgrade
# For production: restart service
sudo systemctl restart fvctools
```

### 2. Version Management

```bash
# Check current version
fvc --version

# Check installed version
uv pip show fvctools

# List available versions
git tag -l
```

## Related Documentation

- [Quickstart Guide](/openwiki/quickstart.md)
- [Architecture Overview](/openwiki/architecture/overview.md)
- [CLI Tools Reference](/openwiki/architecture/tools.md)
- [Integration Guides](/openwiki/integrations/index.md)
- [Testing Guide](/openwiki/testing/overview.md)

## Quick Reference

| Task | Command |
|------|---------|
| Install dev | `uv pip install -e ".[dev]"` |
| Install prod | `uv pip install .` |
| Run tests | `pytest` |
| Format code | `ruff format src/fvc` |
| Lint code | `ruff check src/fvc` |
| Login CodeArtifact | `source scripts/Login-ToCodeArtifact.sh` |
| Install scripts | `./scripts/Install-FvcTools.sh` |

## Best Practices

✅ **Use virtual environments** for isolation
✅ **Pin dependency versions** for reproducibility
✅ **Test in staging** before production deployment
✅ **Monitor resource usage** in production
✅ **Backup critical data** regularly
✅ **Document configuration** in README
✅ **Use .gitignore** for sensitive files
✅ **Follow security best practices** for credentials

## Next Steps

- **Set up development environment**: Follow [Development Setup](#development-environment-setup)
- **Run tests**: See [Testing Guide](/openwiki/testing/overview.md)
- **Explore CLI tools**: See [CLI Tools Reference](/openwiki/architecture/tools.md)
- **Set up production monitoring**: Configure logging and monitoring
