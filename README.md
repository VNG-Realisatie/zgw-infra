# ZGW Infra

| Key       | Value                                         |
|-----------|-----------------------------------------------|
| Version   | 0.6.0                                         |
| Source    | https://github.com/VNG-Realisatie/zgw-infra   |
| Keywords  | ZGW, kubernetes, helm                         |
| Related   | https://github.com/VNG-Realisatie/gemma-zaken |


## Introductie

Om het zaakgericht werken in de Common Ground architectuuur te ondersteunen zijn de [API's voor Zaakgericht werken ontwikkeld](https://github.com/VNG-Realisatie/gemma-zaken). 

## Aan de slag

De eerste stap om de helm chart te draaien is uiteraard het opzetten van een kubernetes cluster en een lokale versie van helm.
Het is aan de raden een helm versie van `>= 3.8` te nemen omdat deze het toestaat helm charts als oci images te downloaden.

Voor helm zie:

https://github.com/helm/helm/releases
https://helm.sh/docs/intro/install/

Hoe je kubernetes lokaal draait hangt af van je systeem maar gemakshalve worden hier alleen `minikube` en `docker-desktop` behandeld.

### docker-desktop

Docker-desktop is de standaard om kubernetes te draaien op MacOs en Windwos.
Doordat docker-desktop een gui heeft is het voldoende docker-desktop te starten.

Docker-desktop heeft geen eigen ingress dus deze moet je instellen. Hiervoor zit in de `Makefile` een commando:

```shell
make -C helm/ri nginx_install 
```

### minikube

```shell
minikube start --cpus 2 --memory 4000 --driver=hyperkit --container-runtime=docker
minikube addons enable ingress
minikube ip
eval $(minikube docker-env)
```

Deze commando's starten een minikube cluster met docker en hyperkit. Er zijn veel varaianten mogelijk dus dit dient louter als voorbeeld.
Zie bijvoorbeeld [minkube](https://minikube.sigs.k8s.io/docs/start/).

Zorg dat je ingress activeert en het ip-adres van minikube opvraagt (minikube draait immers in een virtuele machine met een eigen IP).
Het IP heb je nodig in de ingress stap.

Mocht je lokaal images willen gebruiken het laatste commando.

Hierna kun je aan de slag!

## Namespace

Voor je de helm chart installeert is het nodig een namespace te maken. Deze staat standaard op `zgw` maar is aan te passen in de `values.yaml`.

Onderstaand commando gaat uit van de standaard:

```shell
kubectl create ns zgw
```

## Parser

De parser is een python script die voor lokaal gebruik een config opbouwt in de `values.yaml`.
De `env.yaml` wordt gebruikt om een configuratie te laden. Standaard wordt `local` genomen maar deze is eenvoudig te overschrijven door:

```shell
export ENV=production
```

te zetten. Of eventueel mee te geven in PyCharm. Daarna is het eenvoudig een kwestie van:

```shell
cd ./parser
pip install -r requirements.txt
python3 parser.py
```

## Lokaal

Als je een nieuwe config hebt gemaakt met de parser kun je de helm chart installeren.

```shell
cd ./helm/ri_zgw
helm install ri_zgw .
```

Het duurt ongeveer 3 minuten voordat alle services up and running zijn. Grofweg zijn er aantal stappen die elke service doorgaat:

1. wachten tot de database beschikbaar is
2. aanmaken van de database
3. migrate van de schemas
4. seeden van initiële data
5. opstarten van de service

Doordat stap 2 faalt als er al een database bestaat (bijvoorbeeld bij een upgrade) zullen de jobs dan falen. 
Bij een upgrade is het dus belangrijk de `createJobs` flag op `false` te zetten.

```shell
cd ./helm/ri
helm install --set global.config.createJobs=false ri .
```

Als de installatie wilt verwijderen kun je het volgende commando gebruiken:

```shell
cd ./helm/ri
helm delete ri
```

Al deze commando's zijn ook teurg te vinden in de `./helm/ri/Makefile`

## Productie

WIP: voor nu wordt de helm chart niet in een productie (like) omgeving uitgerold.

### CICD

Wanneer er een release wordt gemaakt van `zgw-infra` repo wordt er automatisch een nieuwe helm chart gebouwd en opgeslagen in GHCR als `OCI`.

Voor meer details zie ook [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry):

```shell
.github/workflows/ci.yml
```

### pull

Images gemaakt tijdens het cicd proces kunnen gepulled worden als `OCI`. De version kan weggelaten worden voor een latest variant.

```shell
helm pull oci://ghcr.io/vng-realisatie/ri-zgw --version 0.0.6
```

Hiermee wordt de productie versie van de helm chart lokaal neergezet. LET OP hierbij zit uiteraard geen parser!
## Ingress

Om lokaal je ingress in te stellen moeten de dns entries uit de `env.yaml` ook toegevoegd worden aan je `/etc/hosts` afhankelijk van je kubernetes implementatie.
Wederom wordt er hier uitgegaan van `minikube` en `docker-desktop`

### /etc/hosts

De ingress van docker-desktop is normaliter te benaderen via localhost. 

Onderstaand commando gaat uit van de standaard lokale records zoals beschreven in `env.yaml`.  Let op hiervoor zijn sudo rechten nodig!

```shell
export ADDR=127.0.0.1
echo "# RI ingress points
${ADDR} k8s-ac-local.test
${ADDR} k8s-brc-local.test
${ADDR} k8s-contactmomenten-local.test
${ADDR} k8s-drc-local.test
${ADDR} k8s-klanten-local.test
${ADDR} k8s-nrc-local.test
${ADDR} k8s-tokens-local.test
${ADDR} k8s-verzoeken-local.test
${ADDR} k8s-vrl-local.test
${ADDR} k8s-zrc-local.test
${ADDR} k8s-ztc-local.test" | sudo tee -a /etc/hosts
```

Wanneer je minikube gebruikt  dient `127.0.0.1` vervangen te worden door het ip van minikube op te vragen via:

```shell
minikube ip
```

In je browser kun je nu de RI benaderen op bijvoorbeeld:

`http://k8s-ac-local.test`
