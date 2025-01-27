$username = "aws"
$profile_arg = "--profile flyvercity"
$domain_arg = "--domain flyvercity"
$domain_owner_arg = "--domain-owner 368281077578"
$region_arg = "--region eu-west-3"
$format_arg = "--format pypi"
$repository_arg = "--repository common"
$output_arg = "--output text"

$token_command = "aws $profile_arg codeartifact get-authorization-token"
$token_command += " --query authorizationToken"
$token_command += " $domain_arg $domain_owner_arg $region_arg $output_arg" 
$password = Invoke-Expression $token_command
if ($LASTEXITCODE -ne 0) { throw "Failed to get authorization token" }

$endpoint_command = "aws $profile_arg codeartifact get-repository-endpoint"
$endpoint_command += " --query repositoryEndpoint"
$endpoint_command += " $repository_arg"
$endpoint_command += " $format_arg"
$endpoint_command += " $domain_arg $domain_owner_arg $region_arg $output_arg"
$endpoint = Invoke-Expression $endpoint_command
if ($LASTEXITCODE -ne 0) { throw "Failed to get repository endpoint" }

$command = "rye run twine upload --repository-url $endpoint -u $username -p $password .\dist\*"
Invoke-Expression $command
