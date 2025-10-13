# Flyvercity CLI Tools Suite

## Installation

Download and run the `scripts/Install-FvcTools.ps1` script in PowerShell.

## Getting Started

```pwsh
fvc --help
```

## Development Environment

Requires the `uv` package and project management tool.

Generic invocation:

```bash
uv run fvc --help
```

## PowerShell

Load as a PowerShell function:

```pwsh
. .\Load-FvcTools.ps1
```

Use as an object:

```pwsh
(FvcTool <arguments>).<field>
```

Example:

```pwsh
(FvcTool calc undulation 10.0 10.0).undulation
```
