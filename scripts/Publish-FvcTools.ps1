$username = "aws"

$password = $(aws codeartifact get-authorization-token --domain flyvercity --domain-owner 368281077578 --region eu-west-3 --query authorizationToken --output text)
if ($LASTEXITCODE -ne 0) { throw "Failed to get authorization token" }

$endpoint = $(aws codeartifact get-repository-endpoint --domain flyvercity --domain-owner 368281077578 --repository common --region eu-west-3 --format pypi --query repositoryEndpoint --output text)
if ($LASTEXITCODE -ne 0) { throw "Failed to get repository endpoint" }

$command = "rye run twine upload --repository-url $endpoint -u $username -p $password .\dist\*"
Invoke-Expression $command
