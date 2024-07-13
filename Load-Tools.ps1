function Add-Prefix([string]$prefix, [string]$path) {
    $i = Get-Item $path
    return "$($i.Directory)\$($prefix)_$($i.Name)"
}

Set-Alias -Name fvc -Value .\Run-FvcTools
