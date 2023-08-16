# ZGW Infra

| Key       | Value                                         |
|-----------|-----------------------------------------------|
| Version   | 0.6.0                                         |
| Source    | https://github.com/VNG-Realisatie/zgw-infra   |
| Keywords  | ZGW, kubernetes, helm                         |
| Related   | https://github.com/VNG-Realisatie/gemma-zaken |


# Table of Contents
1. [ZGW Infra](#zgw-infra)
2. [Introductie](#introductie)
3. [Aan de slag](#aan-de-slag)
   1. [Toegang tot het cluster](#toegang-tot-het-cluster)
   2. [Lokaal](#lokaal)
      1. [docker-desktop](#docker-desktop)
      2. [minikube](#minikube)
      3. [Namespace](#namespace)
   3. [Parser](#parser)
4. [Productie](#productie)
5. [CICD](#cicd)
   1. [Test](#test)
   2. [Productie](#productie-cicd)
   3. [pull](#pull)
6. [Ingress](#ingress)
   1. [/etc/hosts](#etchosts)
7. [Secrets](#secrets)


## Introductie

Om het zaakgericht werken in de Common Ground architectuuur te ondersteunen zijn de [API's voor Zaakgericht werken ontwikkeld](https://github.com/VNG-Realisatie/gemma-zaken). 

## Aan de slag

Hierbij een omschrijving wat er moet gebeuren wanneer je de helm chart wilt gebruiken op een lokaal en het productie systeem.
Let er op dat deze omschrijving(en) gedaan zijn vanuit macos en er daarmee vanuit gaan dat je een terminal hebt en weet hoe je deze gebruikt.

Windows wordt hierin NIET meegenomen. Wanneer je toch Windows gebruikt wordt het aangeraden `WSL` te gebruiken zodat alle commando's vanuit een linux omgeving gedraaid kunnen worden.

### Toegang tot het cluster

Volg de insctructies op (login via gitlab nodig!):

https://auth.haven.vng.cloud/

## Lokaal

De eerste stap om de helm chart te draaien is uiteraard het opzetten van een kubernetes cluster en een lokale versie van helm.
Het is aan de raden een helm versie van `>= 3.8` te nemen omdat deze het toestaat helm charts als oci te downloaden.

Voor helm zie:

https://github.com/helm/helm/releases
https://helm.sh/docs/intro/install/

Hoe je kubernetes lokaal draait hangt af van je systeem maar gemakshalve worden hier alleen `minikube` en `docker-desktop` behandeld.

### docker-desktop

Docker-desktop is de standaard om kubernetes te draaien op MacOs en Windwos (via een VM).
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

Mocht je lokaal images willen gebruiken dient de `Makefile` in de root als voorbeeld (minikube staat toe images van lokaal naar de VM te "loaden").

Hierna kun je aan de slag!

### Namespace

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

Als je een nieuwe config hebt gemaakt met de parser kun je de helm chart installeren.

```shell
cd ./helm/ri-zgw
helm install ri-zgw .
```

Het duurt ongeveer 3 minuten voordat alle services up and running zijn. Grofweg zijn er aantal stappen die elke service doorgaat:

1. wachten tot de database beschikbaar is
2. aanmaken van de database
3. migrate van de schemas
4. seeden van initiële data
5. opstarten van de service

Als de installatie wilt verwijderen kun je het volgende commando gebruiken:

```shell
cd ./helm/ri-zgw
helm delete ri-zgw
```

Al deze commando's zijn ook teurg te vinden in de `./helm/ri-zgw/Makefile`

### ImageTags

Alle image tags zijn aan te passen in `./parser/env.yaml` deze versie worden door de parser opgepakt en in alle helm charts verspreid.
Wanneer er dus een productie release plaats moet vinden zijn er de volgende stappen.

Voorbeeld. ZRC gaat naar versie `10.1.231`.

```shell
git checkout -b release/summer-time
```

Pas dan de versie aan in `./parser/env.yaml` :

```yaml
zrc:
  repo: ghcr.io/vng-realisatie/zaken-api
  local:
    tag: pr-267
    ingressHost: k8s-zrc-local.test
  test:
    tag: sha-279ce65
    ingressHost: zaken-api.test.vng.cloud
  production:
    tag: 10.1.231
    ingressHost: zaken-api.vng.cloud
```

Hierna moet je de gitflow volgen: commit - push - pull request - merge naar main.

Als dit op main staat kun je via github (of de cli) een nieuwe release aanmaken vanaf main.

Hierna wordt de versie automatisch uitgerold (zie hieronder).

## Productie

Op productie hebben wij momenteel 2 omgevingen `zgw-test` en `zgw` waarbij de laatste de prod omgeving is.

`zgw-test` is verbonden aan de `OCI` `ri-zgw-test` - https://github.com/VNG-Realisatie/zgw-infra/pkgs/container/ri-zgw-test

`zgw` is verbonden aan de `OCI` `ri-zgw` - https://github.com/VNG-Realisatie/zgw-infra/pkgs/container/ri-zgw

Doordat alles wat wij hebben in flux staat heb je met dit gedeelte als het goed is weinig te maken. Elke 5 minuten wordt er vanuit flux gekeken of er een nieuwe `OCI` aanwezig is.
Wanneer deze gevonden is wordt deze automatisch gedeployed.

Voor voorbeelden en verdere beschrijvingen zie:

`./flux`

en

`./flux/README.md`

## CICD

Voor meer details zie ook [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

### Test

Wanneer er een PR wordt gemaakt zal hier een helm chart voor worden gebouwd en gepushed als `OCI` naar:

https://github.com/VNG-Realisatie/zgw-infra/pkgs/container/ri-zgw-test

Wil je iets aan de versies aanpassen dan moet dat in `parser.py`:

```python
    if env == "test":
        if stripped == "":
            # GITHUB_REF_NAME contains the PR number
            branch = os.getenv("GITHUB_REF_NAME")
            version = branch.split("/")[0]
            semver = f"0.{version}.0"
            stripped = semver
```

`version` is hier het versie nummer van de PR. Doordat deze uniek is opgehoogd wordt wordt eer altijd een nieuwe `OCI` gebouwd. Door dit schema is het wel zo dat deze altijd major en patch 0 hebben.

### Productie

Wanneer er een release wordt gemaakt van `zgw-infra` repo wordt er automatisch een nieuwe helm chart gebouwd en opgeslagen in GHCR als `OCI`.

https://github.com/VNG-Realisatie/zgw-infra/pkgs/container/ri-zgw

Wil je iets aan de versies aanpassen dan moet dat in `parser.py`:

```python
    if env == "production":
        if stripped == "":
            # GITHUB_REF_NAME is the name of a release when using github
            branch = os.getenv("GITHUB_REF_NAME")
            stripped = branch
```

`stripped` is hierin de naam van de release die gedaan is. Dit is dan ook de versie van de helm chart. Hierdoor is productie altijd gelinkt aan de releases van `zgw-infra`:

https://github.com/VNG-Realisatie/zgw-infra/releases

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

## Secrets

Het bewaken en uitrollen van secrets is altijd een uitdaging maar hier is gekozen voor `kubeseal`.
Voor installatie zie:

https://github.com/bitnami-labs/sealed-secrets#helm-chart

en

`./flux/README.md`

## Migrated

Deze folder bestaat uit legacy manieren om lokaal en op kubernetes te deployen. Deze zouden <b>NIET</b> meer gebruikt moeten worden.
