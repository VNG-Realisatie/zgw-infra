HELM_CHART_NAME=zgw-secrets

helm_lint:
	helm lint .

helm_dry_run:
	helm install ${HELM_CHART_NAME} -f values-secret-overwrite.yaml --dry-run .

helm_dry_run_output:
	helm install ${HELM_CHART_NAME}  -f values-secret-overwrite.yaml --dry-run . > test.yaml

helm_install:
	helm install ${HELM_CHART_NAME} -f values-secret-overwrite.yaml .

helm_upgrade:
	helm upgrade --install ${HELM_CHART_NAME} -f values-secret-overwrite.yaml .

helm_delete:
	helm delete ${HELM_CHART_NAME}

encrypt:
	gpg -c values-secret-overwrite.yaml

decrypt:
	gpg -d values-secret-overwrite.yaml.gpg