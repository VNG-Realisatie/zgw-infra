NGINX_VERSION:=4.0.19
NGINX_NAMESPACE:=nginx-ingress

install_with_overwrite:
	helm install ri -f values-secret-overwrite.yaml .

helm_dry_run:
	helm install ri -f values-secret-overwrite.yaml --dry-run .

helm_dry_run_output:
	helm install ri -f values-secret-overwrite.yaml --dry-run . > test.yaml

gpg_encode:
	gpg -c values-secret-overwrite.yaml

gpg_decode:
	gpg -d values-secret-overwrite.yaml.gpg

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

create_local_dns_entries:
	echo "not yet implemented"