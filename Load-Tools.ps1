function Invoke-FvcTools 
{
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$listArgs
    )

    return $(rye run fvc @listArgs)
}

function FvcTool {
    $result = $(Invoke-FvcTools --json --no-pprint @args)
    return ConvertFrom-Json -InputObject $result
}

Set-Alias -Name fvc -Value Invoke-FvcTools
