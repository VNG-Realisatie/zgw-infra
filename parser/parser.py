#!/usr/bin/env python3
import subprocess
import os
import yaml


def get_version():
    """Gets the latest git tag, strips and returns it"""
    output = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], capture_output=True
    ).stdout.decode("utf-8")
    stripped = output.strip("\n")
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
                print(chart)
                yaml.dump(chart, write_path, sort_keys=True)
        except yaml.YAMLError as exc:
            print(exc)
    return


def push_helm_chart_to_museum(package_name):
    """
    helm push <chart-name>-${CHART_VERSION}.tgz oci://ghcr.io/<GITHUB-USERNAME>
    """
    print(package_name)
    return


def create_helm_package(path):
    """Package parsed helm chart in /tmp/ to be uploaded"""
    output = subprocess.run(
        ["helm", "package", path, "--destination=/tmp/"], capture_output=True
    ).stdout.decode("utf-8")
    print(output)
    return


def set_versions(env, cwd, helm_path, version):
    chart_name = "Chart.yaml"
    values_name = "values.yaml"
    sub_chart = "charts"

    root_chart = os.path.join(helm_path, chart_name)
    root_values = os.path.join(helm_path, values_name)
    parse_chart_version(version=version, file_path=root_chart)

    file_path = os.path.join(cwd, f"{env}.yaml")
    with open(file_path, "r") as stream:
        try:
            images = yaml.load(stream, Loader=yaml.FullLoader)
            for image in images:
                tag = images[image]["tag"]

                if image == "tokenSeeder":
                    with open(root_values, "r") as stream:
                        try:
                            values = yaml.load(stream, Loader=yaml.FullLoader)
                            values["global"][image]["tag"] = tag
                            with open(root_values, "w") as write_path:
                                print(values)
                                yaml.dump(values, write_path, sort_keys=True)
                        except yaml.YAMLError as exc:
                            print(exc)
                    continue

                api_path = os.path.join(helm_path, sub_chart, image)
                chart_path = os.path.join(api_path, chart_name)
                values_path = os.path.join(api_path, values_name)

                with open(values_path, "r") as stream:
                    try:
                        values = yaml.load(stream, Loader=yaml.FullLoader)
                        values["service"]["images"]["tag"] = tag
                        with open(values_path, "w") as write_path:
                            print(values)
                            yaml.dump(values, write_path, sort_keys=True)
                    except yaml.YAMLError as exc:
                        print(exc)

                with open(chart_path, "r") as stream:
                    try:
                        chart = yaml.load(stream, Loader=yaml.FullLoader)
                        chart["appVersion"] = tag
                        chart["version"] = version
                        with open(chart_path, "w") as write_path:
                            print(values)
                            yaml.dump(chart, write_path, sort_keys=True)
                    except yaml.YAMLError as exc:
                        print(exc)

        except yaml.YAMLError as exc:
            print(exc)
    return


if __name__ == "__main__":
    env = os.getenv("ENV", "test")
    cwd = os.getcwd()
    if cwd.split("/")[-1] != "parser":
        cwd = os.path.join(cwd, "parser")
    tagged_version = get_version()
    helm_path = get_helm_path(cwd)
    set_versions(env=env, cwd=cwd, helm_path=helm_path, version=tagged_version)
    create_helm_package(helm_path)
    helm_package_name = "ri-%s.tgz" % tagged_version
    push_helm_chart_to_museum(helm_package_name)
