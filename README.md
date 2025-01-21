# Flyvercity CLI Tools Suite

Requires `rye` project and package management tool.

## Development Environment

Generic invocation:

```bash
rye run fvc --help
```

### PowerShell

Load for PowerShell and create `fvc` alias:

```pwsh
. .\Load-FvcTools
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
