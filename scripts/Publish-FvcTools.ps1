$username = "aws"
$profile_arg = "--profile flyvercity"
$domain_arg = "--domain flyvercity"
$domain_owner_arg = "--domain-owner 368281077578"
$region_arg = "--region eu-west-3"
$format_arg = "--format pypi"
$repository_arg = "--repository common"
$output_arg = "--output text"

$token_command = @(
    "aws $profile_arg codeartifact get-authorization-token"
    "--query authorizationToken"
    "$domain_arg $domain_owner_arg $region_arg $output_arg"
)
$password = Invoke-Expression ($token_command -join " ")
if ($LASTEXITCODE -ne 0) { throw "Failed to get authorization token" }

$endpoint_command = @(
    "aws $profile_arg codeartifact get-repository-endpoint"
    "--query repositoryEndpoint"
    "$repository_arg $format_arg $domain_arg $domain_owner_arg $region_arg $output_arg"
)
$endpoint = Invoke-Expression ($endpoint_command -join " ")
if ($LASTEXITCODE -ne 0) { throw "Failed to get repository endpoint" }

$command = "uv publish --publish-url $endpoint -u $username -p $password .\dist\*"
Write-Host Running: $command
Invoke-Expression $command
