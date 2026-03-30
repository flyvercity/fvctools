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

Write-Host 'Setting environment variables for CodeArtifact authentication'

$env:UV_INDEX_CODEARTIFACT_USERNAME = $username
$env:UV_INDEX_CODEARTIFACT_PASSWORD = $password
$env:UV_PUBLISH_USERNAME = $username
$env:UV_PUBLISH_PASSWORD = $password
