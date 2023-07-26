#!/bin/bash

# Set the GitHub PAT and the secret name and namespace
secret_name="ghcr-auth"
namespace="zgw"
pub_file="pub-sealed-secrets.pem"

# Function to update the github.yaml secret
update_github_secret() {
    local secret_file=$1
    local updated_secret_file="${secret_file%.yaml}.yaml"

    # Update the secret using kubectl
    kubectl create secret docker-registry "$secret_name" \
        --namespace="$namespace" \
        --docker-username=flux \
        --docker-password="$github_pat" \
        --docker-server=ghcr.io \
        --output=yaml --dry-run=client \
        > "$updated_secret_file"

}

# Check if the GITHUB_PAT environment variable is set
if [ -z "$GITHUB_PAT" ]; then
    echo "Error: GITHUB_PAT environment variable is not set"
    exit 1
fi

# Retrieve the GitHub PAT from the environment variable
github_pat="$GITHUB_PAT"

# Update the github.yaml secret
update_github_secret "github.yaml"
