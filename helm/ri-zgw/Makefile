NGINX_VERSION:=4.0.19
NGINX_NAMESPACE:=nginx-ingress
HELM_CHART_NAME=zgw

helm_lint:
	helm lint .

helm_dry_run:
	helm install ${HELM_CHART_NAME} --dry-run .

helm_dry_run_output:
	helm install ${HELM_CHART_NAME} --dry-run . > test.yaml

helm_install:
	helm install ${HELM_CHART_NAME} .

helm_upgrade:
	helm upgrade --install ${HELM_CHART_NAME} --set global.config.createJobs=false .

helm_delete:
	helm delete ${HELM_CHART_NAME}

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
