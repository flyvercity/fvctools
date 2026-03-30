#!/bin/bash

# Ensure required environment variables are set
if [ -z "$UV_INDEX_CODEARTIFACT_PASSWORD" ]; then
    echo "Error: UV_INDEX_CODEARTIFACT_PASSWORD is not set. Run 'source scripts/Login-ToCodeArtifact.sh' first."
    exit 1
fi

# Construct URL and perform installation
UV_INDEX_URL="https://aws:${UV_INDEX_CODEARTIFACT_PASSWORD}@flyvercity-368281077578.d.codeartifact.eu-west-3.amazonaws.com/pypi/tools/simple/"

echo "Installing fvctools from CodeArtifact..."

uv tool install fvctools \
    --index "$UV_INDEX_URL" \
    --prerelease=allow \
    --extra-index-url https://pypi.org/simple
