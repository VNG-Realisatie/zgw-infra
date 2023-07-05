#!/bin/bash

# Get the directory of the script
script_directory=$(dirname "$(readlink -f "$0")")

# Check if the Kubernetes context is set to "pinniped-azure-common-prod"
current_context=$(kubectl config current-context)
expected_context="pinniped-azure-common-prod"

if [[ "$current_context" != "$expected_context" ]]; then
    echo "Error: Kubernetes context is not set to '$expected_context'. Please set the correct context."
    exit 1
fi

# Set the controller name and namespace
controller_name="sealed-secrets-controller"
controller_namespace="zgw"

# Fetch the certificate
kubeseal --fetch-cert \
  --controller-name="$controller_name" \
  --controller-namespace="$controller_namespace" \
  > "$script_directory/pub-sealed-secrets.pem"

echo "Certificate copied to $script_directory/pub-sealed-secrets.pem"
