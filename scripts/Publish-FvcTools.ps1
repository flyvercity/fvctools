$username = "aws"

$password = $(aws --profile flyvercity codeartifact get-authorization-token --query authorizationToken --domain flyvercity --domain-owner 368281077578 --region eu-west-3 --output text)
if ($LASTEXITCODE -ne 0) { throw "Failed to get authorization token" }

$endpoint = $(aws --profile flyvercity codeartifact get-repository-endpoint --query repositoryEndpoint --repository common --format pypi --domain flyvercity --domain-owner 368281077578 --region eu-west-3 --output text)
if ($LASTEXITCODE -ne 0) { throw "Failed to get repository endpoint" }

uv run twine upload --repository-url $endpoint -u $username -p $password .\dist\*
if ($LASTEXITCODE -ne 0) { throw "Failed to upload fvctools" }
