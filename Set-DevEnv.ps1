function FvcToolsWrapper
{
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$listArgs
    )

    return $(uv run fvc @listArgs)
}

Set-Alias -Name fvc -Value FvcToolsWrapper
