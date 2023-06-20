#!/usr/bin/env python3
import json
import os
import random
import string
import subprocess

import yaml
from django.core.management import utils


def create_random_string(size=12):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(size)
    )


def get_version(env):
    """Gets the latest git tag, strips and returns it"""
    output = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], capture_output=True
    ).stdout.decode("utf-8")
    stripped = output.strip("\n")
    if env == "production":
        if stripped == "":
            # GITHUB_REF_NAME is the name of a release when using github
            branch = os.getenv("GITHUB_REF_NAME")
            stripped = branch
        if stripped.startswith("v"):
            stripped = stripped.split("v")[1]

    if env == "test":
        if stripped == "":
            # GITHUB_REF_NAME contains the PR number
            branch = os.getenv("GITHUB_REF_NAME")
            version = branch.split("/")[0]
            semver = f"0.{version}.0"
            stripped = semver

    if stripped == "":
        stripped = "0.0.1-local"
    print(stripped)

    return stripped


def get_helm_path(cwd):
    """Finds local helm chart and returns it's location"""
    helm_path = os.path.join(cwd, "../helm/ri-zgw")
    return helm_path


def get_secrets_path(cwd):
    """Finds local secrets helm chart and returns it's location"""
    helm_path = os.path.join(cwd, "../helm/secrets")
    return helm_path


def parse_chart_version(version, file_path, env):
    dependencies = "dependencies"
    with open(file_path, "r") as stream:
        try:
            chart = yaml.load(stream, Loader=yaml.FullLoader)
            chart["version"] = version
            chart["name"] = "ri-zgw"
            if env == "test":
                chart["name"] = "ri-zgw-test"
            if dependencies in chart:
                for dependency in chart[dependencies]:
                    dependency["version"] = version
            with open(file_path, "w") as write_path:
                yaml.dump(chart, write_path, sort_keys=True)
        except yaml.YAMLError as exc:
            print(exc)
    return


def set_versions(env, cwd, helm_path, version):
    """
    will loop over all subcharts and set the config tags as appVersion loaded from the env.yaml
    Upgrades the chart versions to the released version or the latest tag (for local development)

    :param env: env to load from yaml
    :param cwd: current working dir
    :param helm_path: path to the helm chart
    :param version: version to set in the Chart.yaml
    :return:
    """
    chart_name = "Chart.yaml"
    values_name = "values.yaml"
    sub_chart = "charts"
    fixed_prod_kube_version = "1.23.8"
    namespace = ""
    vng_repos = ["ghcr.io/vng-realisatie"]

    root_chart = os.path.join(helm_path, chart_name)
    root_values = os.path.join(helm_path, values_name)
    parse_chart_version(version=version, file_path=root_chart, env=env)

    file_path = os.path.join(cwd, "env.yaml")
    with open(file_path, "r") as stream:
        try:
            env_file = yaml.load(stream, Loader=yaml.FullLoader)
            configs = env_file[env]
            for config in configs:
                with open(root_values, "r") as stream:
                    try:
                        if config == "namespace":
                            continue
                        values = yaml.load(stream, Loader=yaml.FullLoader)
                        if configs["namespace"] != "":
                            values["global"]["namespace"] = configs["namespace"]
                        namespace = values["global"]["namespace"]
                        for v in configs[config]:
                            if type(configs[config][v]) == bool:
                                values["global"]["config"][v] = configs[config][v]
                            else:
                                if env == "local":
                                    for inner_value in configs[config][v]:
                                        if configs[config][v][inner_value] == "":
                                            password = create_random_string(24)
                                            values["global"][v][inner_value] = password

                        if env == "local":
                            output = subprocess.run(
                                ["kubectl", "config", "current-context"],
                                capture_output=True,
                            ).stdout.decode("utf-8")
                            kube_context = output.strip("\n")

                            short_kube = subprocess.run(
                                ["kubectl", "version", "--short", "-o", "json"],
                                capture_output=True,
                            ).stdout.decode("utf-8")

                            json_version = json.loads(short_kube)
                            kube_version = json_version["serverVersion"]["gitVersion"]

                            values["global"]["config"]["environment"] = kube_context
                            values["global"]["config"]["kube"] = kube_version

                            for api in values["global"]["secret_keys"]:
                                random_key = utils.get_random_secret_key()
                                values["global"]["secret_keys"][api] = random_key

                        else:
                            values["global"]["config"]["kube"] = fixed_prod_kube_version
                            values["global"]["config"]["environment"] = env
                        with open(root_values, "w") as write_path:
                            yaml.dump(values, write_path, sort_keys=True)
                    except yaml.YAMLError as exc:
                        print(exc)
        except yaml.YAMLError as exc:
            print(exc)

        for api in env_file:
            try:
                tag = env_file[api][env]["tag"]
                image_repo = env_file[api]["repo"].lower()
            except KeyError:
                continue

            if api == "tokenSeeder":
                with open(root_values, "r") as stream:
                    try:
                        values = yaml.load(stream, Loader=yaml.FullLoader)
                        values["global"][api]["tag"] = tag
                        values["global"][api]["imageRepo"] = image_repo
                        values["global"][api]["imagePullPolicy"] = "Never"
                        for official_repo in vng_repos:
                            if official_repo in image_repo:
                                values["global"][api]["pullPolicy"] = "Always"
                                break
                        with open(root_values, "w") as write_path:
                            yaml.dump(values, write_path, sort_keys=True)
                    except yaml.YAMLError as exc:
                        print(exc)
                continue

            try:
                ingress_entry = env_file[api][env]["ingressHost"]
            except KeyError:
                print("an unexpected field was found in your env.yaml")
                continue

            api_path = os.path.join(helm_path, sub_chart, api)
            chart_path = os.path.join(api_path, chart_name)
            values_path = os.path.join(api_path, values_name)

            with open(values_path, "r") as stream:
                try:
                    values = yaml.load(stream, Loader=yaml.FullLoader)
                    values["service"]["images"]["tag"] = tag
                    values["service"]["images"]["imageRepo"] = image_repo
                    service_name = values["service"]["name"]
                    internal_service_address = (
                        f"{service_name}.{namespace}.svc.cluster.local"
                    )
                    host = f"{ingress_entry},localhost,{service_name},{internal_service_address}"
                    values["config"]["host"] = host
                    values["config"]["pullPolicy"] = "Never"
                    try:
                        if values["config"]["env"]:
                            values["config"]["env"] = env
                            if service_name == "token-issuer":
                                values["config"]["env"] = "kubernetes"
                    except KeyError:
                        pass
                    for official_repo in vng_repos:
                        if official_repo in image_repo:
                            values["config"]["pullPolicy"] = "Always"
                            break

                    with open(values_path, "w") as write_path:
                        yaml.dump(values, write_path, sort_keys=True)
                except yaml.YAMLError as exc:
                    print(exc)

            with open(chart_path, "r") as stream:
                try:
                    chart = yaml.load(stream, Loader=yaml.FullLoader)
                    chart["appVersion"] = tag
                    chart["version"] = version
                    with open(chart_path, "w") as write_path:
                        yaml.dump(chart, write_path, sort_keys=True)
                except yaml.YAMLError as exc:
                    print(exc)

            with open(root_values, "r") as stream:
                try:
                    values = yaml.load(stream, Loader=yaml.FullLoader)
                    if api == "vrl":
                        vrl_fixture = {'host': 'referentielijsten-api.vng.cloud', 'name': 'vrl', 'port': 8000}
                        found = any(api in d.values() for d in values['ingress']['services'])
                        if not found:
                            if env == "test":
                                break
                            values["ingress"]["services"].append(vrl_fixture)

                    svc = next(
                        service
                        for service in values["ingress"]["services"]
                        if service["name"] == api
                    )
                    svc["host"] = ingress_entry
                    if api == "vrl" and env == "test":
                        values["ingress"]["services"].remove(svc)


                    with open(root_values, "w") as write_path:
                        yaml.dump(values, write_path, sort_keys=True)
                except yaml.YAMLError as exc:
                    print(exc)

    return


def generate_secret_values(helm_path, encrypt_key):
    """
    Will set secrets and version for secret helm chart

    :param helm_path: path to the helm chart
    :return:
    """

    namespace = os.getenv("NAMESPACE", "zgw")

    values_name = "values-secret-overwrite.yaml"
    encrypted_overwrite_values = os.path.join(helm_path, values_name)
    echo = subprocess.Popen(("echo", encrypt_key), stdout=subprocess.PIPE)
    subprocess.check_output(
        (
            "gpg",
            "-d",
            "--batch",
            "--yes",
            "--passphrase-fd",
            "0",
            "--output",
            encrypted_overwrite_values,
            f"{encrypted_overwrite_values}.gpg",
        ),
        stdin=echo.stdout,
    )
    echo.wait()

    with open(encrypted_overwrite_values, "r") as stream:
        try:
            values = yaml.load(stream, Loader=yaml.FullLoader)
            for api in values["secret_keys"]:
                random_key = utils.get_random_secret_key()
                values["secret_keys"][api] = random_key
            postgres_password = create_random_string(24)
            values["postgres"]["password"] = postgres_password
            rabbit_password = create_random_string(24)
            values["rabbitmq"]["default_password"] = rabbit_password
            token_issuer = create_random_string(24)
            values["tokenIssuer"]["secret"] = token_issuer
            token_seeder = create_random_string(24)
            values["tokenSeeder"]["secret"] = token_seeder

            print(token_seeder)
            values["namespace"] = namespace

            with open(encrypted_overwrite_values, "w") as write_path:
                yaml.dump(values, write_path, sort_keys=True)

        except yaml.YAMLError as exc:
            print(exc)

    echo = subprocess.Popen(("echo", encrypt_key), stdout=subprocess.PIPE)
    subprocess.check_output(
        (
            "gpg",
            "-c",
            "--batch",
            "--yes",
            "--passphrase-fd",
            "0",
            encrypted_overwrite_values,
        ),
        stdin=echo.stdout,
    )
    echo.wait()
    return


if __name__ == "__main__":
    env = os.getenv("ENV", "local")
    encrypt_key = os.getenv("ENCRYPT_KEY")
    cwd = os.getcwd()
    if cwd.split("/")[-1] != "parser":
        cwd = os.path.join(cwd, "parser")

    tagged_version = get_version(env)
    helm_path = get_helm_path(cwd)

    if encrypt_key is not None:
        helm_path = get_secrets_path(cwd)
        generate_secret_values(helm_path, encrypt_key)
        exit(0)

    set_versions(env=env, cwd=cwd, helm_path=helm_path, version=tagged_version)
