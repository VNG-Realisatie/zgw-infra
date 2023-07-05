#!/bin/bash

# Set the environment variable for test
export ENV="test"

# Run the Python parser for test environment
python parser.py

# Run Helm install dry-run with value-overwrite.yaml for test environment and capture the output
TEST_OUTPUT=$(cd ../helm/ri-zgw && helm install --dry-run --values values-secret-overwrite.yaml --generate-name .)

# Extract the part starting from "# Source: ri-zgw/templates/secrets/secret.yaml" and excluding the "---"
TEST_SECRET_MANIFEST=$(echo "$TEST_OUTPUT" | sed -n '/# Source: ri-zgw-test\/templates\/secrets\/secret.yaml/,/---/p' | sed '$d')

# Set the environment variable for production
export ENV="production"

# Run the Python parser for production environment
python parser.py

# Run Helm install dry-run with value-overwrite.yaml for production environment and capture the output
PRODUCTION_OUTPUT=$(cd ../helm/ri-zgw && helm install --dry-run --values values-secret-overwrite.yaml --generate-name .)

# Extract the part starting from "# Source: ri-zgw/templates/secrets/secret.yaml" and excluding the "---"
PRODUCTION_SECRET_MANIFEST=$(echo "$PRODUCTION_OUTPUT" | sed -n '/# Source: ri-zgw\/templates\/secrets\/secret.yaml/,/---/p' | sed '$d')

# Save the secret manifests to the destination directory
echo "$TEST_SECRET_MANIFEST" > ../flux/zgw-test-secrets.yaml
echo "$PRODUCTION_SECRET_MANIFEST" > ../flux/zgw-secrets.yaml

# Set the environment variable for production
export ENV="local"

# Run the Python parser for production environment
python parser.py