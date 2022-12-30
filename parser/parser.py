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


def get_version():
    """Gets the latest git tag, strips and returns it"""
    output = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], capture_output=True
    ).stdout.decode("utf-8")
    stripped = output.strip("\n")
    if stripped == "":
        # GITHUB_REF_NAME is the name of a release when using github
        branch = os.getenv("GITHUB_REF_NAME")
        stripped = branch
    if stripped.startswith("v"):
        stripped = stripped.split("v")[1]
    if stripped == "":
        stripped = "0.0.1-local"
    print(stripped)
    return stripped


def get_helm_path(cwd):
    """Finds local helm chart and returns it's location"""
    helm_path = os.path.join(cwd, "../helm/ri")
    return helm_path


def parse_chart_version(version, file_path):
    dependencies = "dependencies"
    with open(file_path, "r") as stream:
        try:
            chart = yaml.load(stream, Loader=yaml.FullLoader)
            chart["version"] = version
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
    dummy_sentry_dsn = "https://public@sentry.example.com/1"

    root_chart = os.path.join(helm_path, chart_name)
    root_values = os.path.join(helm_path, values_name)
    parse_chart_version(version=version, file_path=root_chart)

    file_path = os.path.join(cwd, "env.yaml")
    with open(file_path, "r") as stream:
        try:
            env_file = yaml.load(stream, Loader=yaml.FullLoader)
            configs = env_file[env]
            for config in configs:

                if config == "global":
                    with open(root_values, "r") as stream:
                        try:
                            values = yaml.load(stream, Loader=yaml.FullLoader)
                            for v in configs[config]:
                                if type(configs[config][v]) == bool:
                                    values["global"]["config"][v] = configs[config][v]
                                else:
                                    if env == "local":
                                        for inner_value in configs[config][v]:
                                            if configs[config][v][inner_value] == "":
                                                password = create_random_string(24)
                                                values["global"][v][
                                                    inner_value
                                                ] = password

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

                                for api in values["global"]["sentry_dsn"]:
                                    values["global"]["sentry_dsn"][api] = dummy_sentry_dsn
                            else:
                                values["global"]["config"]["kube"] = fixed_prod_kube_version
                                values["global"]["config"]["environment"] = env
                            with open(root_values, "w") as write_path:
                                yaml.dump(values, write_path, sort_keys=True)
                        except yaml.YAMLError as exc:
                            print(exc)
                    continue

                tag = configs[config]["tag"]

                if config == "tokenSeeder":
                    with open(root_values, "r") as stream:
                        try:
                            values = yaml.load(stream, Loader=yaml.FullLoader)
                            values["global"][config]["tag"] = tag
                            with open(root_values, "w") as write_path:
                                yaml.dump(values, write_path, sort_keys=True)
                        except yaml.YAMLError as exc:
                            print(exc)
                    continue

                try:
                    host = configs[config]["host"]
                    ingress_entry = configs[config]["ingressHost"]
                except KeyError:
                    print("an unexpected field was found in your env.yaml")
                    continue

                api_path = os.path.join(helm_path, sub_chart, config)
                chart_path = os.path.join(api_path, chart_name)
                values_path = os.path.join(api_path, values_name)

                with open(values_path, "r") as stream:
                    try:
                        values = yaml.load(stream, Loader=yaml.FullLoader)
                        values["service"]["images"]["tag"] = tag
                        values["config"]["host"] = host

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

                        svc = next(
                            service
                            for service in values["ingress"]["services"]
                            if service["name"] == config
                        )
                        svc["host"] = ingress_entry

                        with open(root_values, "w") as write_path:
                            yaml.dump(values, write_path, sort_keys=True)
                    except yaml.YAMLError as exc:
                        print(exc)

        except yaml.YAMLError as exc:
            print(exc)
    return


if __name__ == "__main__":
    env = os.getenv("ENV", "local")
    cwd = os.getcwd()
    if cwd.split("/")[-1] != "parser":
        cwd = os.path.join(cwd, "parser")

    tagged_version = get_version()
    helm_path = get_helm_path(cwd)
    set_versions(env=env, cwd=cwd, helm_path=helm_path, version=tagged_version)
