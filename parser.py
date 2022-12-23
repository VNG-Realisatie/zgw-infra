#!/usr/bin/env python3
import subprocess
import os
import pip


def get_version():
    """Gets the latest git tag, strips and returns it"""
    output = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], capture_output=True
    ).stdout.decode("utf-8")
    stripped = output.strip("\n")
    print(stripped)
    return stripped


def get_helm_path():
    """Finds local helm chart and returns it's location"""
    cwd = os.getcwd()
    helm_path = os.path.join(cwd, "helm/ri")
    return helm_path


def loop_over_charts(helm_path, version):
    """Replaces helm Chart version and updates the dependencies"""
    chart_name = "Chart.yaml"
    sub_charts = os.path.join(helm_path, "charts")

    for filename in os.listdir(helm_path):
        f = os.path.join(helm_path, filename)
        if os.path.isfile(f) and chart_name in f:
            parse_chart_version(version=version, file_path=f)

    for sub in os.listdir(sub_charts):
        sub_path = os.path.join(sub_charts, sub)
        for filename in os.listdir(sub_path):
            f = os.path.join(sub_path, filename)
            if os.path.isfile(f) and chart_name in f:
                parse_chart_version(version=version, file_path=f)

    return helm_path


def parse_chart_version(version, file_path):
    import yaml

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
    curl --request POST \
     --form 'chart=@mychart-0.1.0.tgz' \
     --user <username>:<access_token> \
     https://gitlab.example.com/api/v4/projects/<project_id>/packages/helm/api/<channel>/charts
    """
    print(package_name)
    return


def install(package):
    """Installs required packages without using a VENV or requirements"""
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])


def create_helm_package(path):
    """Package parsed helm chart in /tmp/ to be uploaded"""
    output = subprocess.run(
        ["helm", "package", path, "--destination=/tmp/"], capture_output=True
    ).stdout.decode("utf-8")
    print(output)
    return


if __name__ == "__main__":
    install("PyYAML")
    tagged_version = get_version()
    helm_path = get_helm_path()
    loop_over_charts(helm_path=helm_path, version=tagged_version)
    create_helm_package(helm_path)
    helm_package_name = "ri-%s.tgz" % tagged_version
    push_helm_chart_to_museum(helm_package_name)
