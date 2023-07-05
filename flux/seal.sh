#!/bin/bash

# Check if kubeseal is installed
if ! command -v kubeseal > /dev/null; then
    echo "Error: kubeseal is not installed. Please install kubeseal and try again."
    exit 1
fi

# Set the paths to your secrets files
github_secret_path="github.yaml"
secrets_path="zgw-secrets.yaml"
secrets_test_path="zgw-test-secrets.yaml"
pub_file="pub-sealed-secrets.pem"

# Function to seal a secret using kubeseal
seal_secret() {
    local secret_file=$1
    local sealed_file="${secret_file%.yaml}.sealed.yaml"

    # Use kubeseal to seal the secret
    kubeseal --format=yaml --cert="$pub_file" < "$secret_file" > "$sealed_file"
    echo "Sealed secret: $sealed_file"
}

# Seal the github secret
seal_secret "$github_secret_path"

# Seal the prod secrets secret
seal_secret "$secrets_path"

# Seal the test secrets secret
seal_secret "$secrets_test_path"
