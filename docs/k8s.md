
Below steps have quite a bit of variation to them depending on where you are running kubernetes.
But assuming you are installing without an ingress the following steps should be followed:

#### kubernetes

```shell
cd ${YOUR_WORKING_DIR}/zaken-api/infra
kubectl create -f k8s
```

#### helm

When using `helm` make sure to populate the values with the proper values and create your secrets values (which have to be base64 encoded):

```shell
echo 'MYPASSWORD' | base64
```

Copy the value that was printed in the output (assuming you are using the example `TVlQQVNTV09SRAo=`) and replace the data part of the secret with the value

Another value that you can set is whether if you want to automatically create the correct database. You can do so by setting `job.run` to true in the `values.yaml`
If you do so you can skip the `SQL` step below.

```shell
cd ${YOUR_WORKING_DIR}/zaken-api/infra/helm
helm install postgres ./postgres
```

#### port-forward

you can now port-forward to localhost
```shell
kubectl port-forward svc/postgres 5432:5432
```


#### kubectl

```shell
kubectl exec -it ${PODNAME} -- psql -U ${USERNAME}
CREATE DATABASE zakenapi_db;
exit
```