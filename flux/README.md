# Flux

## Contents

- [Introductie](#introductie)
- [Werking](#werking)
  - [GITHUB_PAT](#github_pat)
  - [PUBLIC_KEY](#public_key)

## Introductie

Flux is een tool voor GitOps die automatisch de inhoud van een Git-repository implementeert op Kubernetes.

## Guides

https://fluxcd.io/flux/guides/sealed-secrets/
https://fluxcd.io/flux/cheatsheets/oci-artifacts/

## Werking

Flux heeft een repo nodig als bron. In ons geval is dat een `OCI` Helm repository.
In het geval van de `secrets` zijn dat gesealde secrets die in de git repository staan.


### GITHUB_PAT

Wanneer er een nieuwe `GITHUB_PAT` is moet deze in de secrets geupdate worden.

> **Waarschuwing:** Het zou veel beter zijn naar de organisatie tokens te gaan.
> Deze zijn nog in BETA en voor nu worden packages niet ondersteunt. Die zijn nu juist nodig.

De `GITHUB_PAT` is nodig voor flux zodat deze de nieuwe `oci helm charts` kan pullen en deployen.

```shell 
export GITHUB_PAT=$YOUR_NEW_GENERATED_TOKEN
./github.sh
./seal.sh
```

Hiermee wordt de nieuwe `GITHUB_PAT` in de env opgeslagen en via de 2 scripts wordt er een sealed secret gemaakt.

De sealed secrets kunnen vervolgens in gitlab komen:

https://gitlab.com/commonground/haven/internal/configuration/-/tree/master/flux/azure-common-prod/zgw


### PUBLIC_KEY

De public key kan in `github` komen. Omdat deze in het cluster leeft en eventueel een update zou kunnen krijgen is deze eenvoudig te updaten.

```shell
./update_pubkey.sh
```