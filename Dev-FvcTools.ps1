function FvcToolsWrapper
{
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$listArgs
    )

    return $(rye run fvc @listArgs)
}

Set-Alias -Name fvc -Value FvcToolsWrapper
