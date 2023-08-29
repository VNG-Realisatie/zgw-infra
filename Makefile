project_name='zaken-api'
image_path :='../${project_name}'
tag='nonotifications'

build_image:
	cd ${image_path} && docker build -t ${project_name}:${tag} .

tag_image:
	docker tag ${project_name}:${tag} local/${project_name}:${tag}

minikube_load:
	minikube image load local/${project_name}:${tag}

clean_pvc:
	kubectl delete pvc drc-private-media
	kubectl delete pvc postgres-pvc

delete_secret:
	kubectl delete secret zgw-secrets

build_and_load: build_image tag_image minikube_load