 $token = $(aws --profile flyvercity codeartifact get-authorization-token --domain flyvercity --domain-owner 368281077578 --region eu-west-3 --query authorizationToken --output text)
if ($LASTEXITCODE -ne 0) { throw "Failed to get authorization token" }

$repo = "https://aws:$token@flyvercity-368281077578.d.codeartifact.eu-west-3.amazonaws.com/pypi/common/simple/"
pip install --index-url $repo fvctools --upgrade
if ($LASTEXITCODE -ne 0) { throw "Failed to install fvctools" }
