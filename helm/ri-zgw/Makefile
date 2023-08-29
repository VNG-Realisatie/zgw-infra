NGINX_VERSION:=4.0.19
NGINX_NAMESPACE:=nginx-ingress
HELM_CHART_NAME=zgw
NAMESPACE=zgw
OCI_VERSION=0.0.29
OCI_REPO=ri-zgw-test

create_namespace:
	kubectl create ns ${NAMESPACE}

helm_lint:
	helm lint .

helm_dry_run:
	helm install ${HELM_CHART_NAME} --dry-run .

helm_dry_run_output:
	helm install ${HELM_CHART_NAME} --dry-run . > test.yaml

helm_install:
	helm install ${HELM_CHART_NAME} .

helm_upgrade:
	helm upgrade --install ${HELM_CHART_NAME} .

helm_install_complete: helm_lint create_namespace helm_install

helm_install_oci:
	helm install ri-zgw oci://ghcr.io/vng-realisatie/${OCI_REPO} --version ${OCI-VERSION} --set global.config.createSecret=true --set global.namespace=${NAMESPACE}

helm_delete:
	helm delete ${HELM_CHART_NAME}

clean_pvc:
	kubectl delete pvc drc-private-media
	kubectl delete pvc postgres-pvc

delete_secret:
	kubectl delete secret zgw-secrets

remove_zgw_install: helm_delete clean_pvc delete_secret

nginx_install:
	kubectl create namespace ${NGINX_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
	helm install ${NGINX_NAMESPACE} --namespace=${NGINX_NAMESPACE} https://github.com/kubernetes/ingress-nginx/releases/download/helm-chart-${NGINX_VERSION}/ingress-nginx-${NGINX_VERSION}.tgz

cert_manager_install:
	helm repo add jetstack https://charts.jetstack.io
	helm repo update
	helm install \
	  cert-manager jetstack/cert-manager \
	  --namespace cert-manager \
	  --create-namespace \
	  --version v1.10.0 \
	  --set installCRDs=true
