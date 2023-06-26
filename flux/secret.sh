#!/bin/bash

SECRET_NAME="ghcr-auth"
NAMESPACE="zgw"

delete_secret() {
  local secret_name=$1
  local namespace=$2

  existing_secret=$(kubectl get secret $secret_name -n $namespace --no-headers=true --ignore-not-found=true)

  if [[ -n $existing_secret ]]; then
    echo "Deleting secret $secret_name in ns $namespace."
    kubectl delete secret $secret_name -n $namespace
  else
    echo "Secret $secret_name does not exist in ns $namespace. Nothing to do."
  fi
}

create_secret() {
  local secret_name=$1
  local namespace=$2
  local github_pat=$3

  flux create secret oci $secret_name \
    --namespace=$namespace \
    --url=ghcr.io \
    --username=flux \
    --password=$github_pat
}

# Check if GITHUB_PAT is provided as an argument, otherwise fetch it from the environment
if [[ -n $1 ]]; then
  GITHUB_PAT=$1
else
  GITHUB_PAT=$GITHUB_PAT_ENV
fi

delete_secret $SECRET_NAME $NAMESPACE
create_secret $SECRET_NAME $NAMESPACE $GITHUB_PAT
