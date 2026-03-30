#!/bin/bash

# Configuration
USERNAME="aws"
PROFILE="flyvercity"
DOMAIN="flyvercity"
DOMAIN_OWNER="368281077578"
REGION="eu-west-3"
REPOSITORY="common"

echo "Fetching CodeArtifact authorization token..."

# Get token
PASSWORD=$(aws codeartifact get-authorization-token \
    --profile "$PROFILE" \
    --domain "$DOMAIN" \
    --domain-owner "$DOMAIN_OWNER" \
    --region "$REGION" \
    --query authorizationToken \
    --output text)

if [ -z "$PASSWORD" ]; then
    echo "Error: Failed to fetch authorization token."
    # Return 1 if sourced, exit 1 if executed
    return 1 2>/dev/null || exit 1
fi

echo "Setting environment variables for CodeArtifact authentication"

export UV_INDEX_CODEARTIFACT_USERNAME="$USERNAME"
export UV_INDEX_CODEARTIFACT_PASSWORD="$PASSWORD"
export UV_PUBLISH_USERNAME="$USERNAME"
export UV_PUBLISH_PASSWORD="$PASSWORD"

echo "Authentication successful. Variables set."
