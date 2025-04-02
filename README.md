# Flyvercity CLI Tools Suite

## Installation

```pwsh
scripts/Install-FvcTools.ps1
```

## Getting Started

```pwsh
fvc --help
```

## Development Environment

Requires `uv` project and package management tool.

Generic invocation:

```bash
uv run fvc --help
```

### PowerShell

Load for PowerShell and create `fvc` alias:

```pwsh
. .\Set-DevEnv.ps1
```

Invoke:

```pwsh
fvc --help
```

Use as an object:

```pwsh
(FvcTool <arguments>).<field>
```

Example:

```pwsh
(FvcTool calc undulation 10.0 10.0).undulation
```
