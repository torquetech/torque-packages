# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import json
import os
import re
import subprocess
import sys

from importlib import metadata

from torque import exceptions
from torque import v1


_URI = r"^[^:]+://"


def package_dist(path: str):
    """TODO"""

    return metadata.Distribution.at(path)


def installed_packages():
    """TODO"""

    packages = {}

    for entry in os.listdir(f"{v1.utils.torque_dir()}/system"):
        if not entry.endswith(".dist-info"):
            continue

        path = f"{v1.utils.torque_dir()}/system/{entry}"
        dist = package_dist(path)

        with open(f"{path}/direct_url.json", encoding="utf-8") as f:
            uri = json.loads(f.read())["url"]

        packages[dist.name] = {
            "version": dist.metadata["Version"],
            "path": path,
            "uri": uri
        }

    return packages


def install_deps():
    """TODO"""

    requirements = []

    for metadata in installed_packages().values():
        dist = package_dist(metadata["path"])
        dist_requires = dist.metadata.get_all("Requires-Dist")

        if dist_requires:
            requirements += dist_requires

    if os.path.isfile(f"{v1.utils.torque_dir()}/requirements.txt"):
        with open(f"{v1.utils.torque_dir()}/requirements.txt", encoding="utf8") as file:
            requirements += [i.strip() for i in file]

    requirements += [""]

    with open(f"{v1.utils.torque_dir()}/local/requirements.txt", "w", encoding="utf8") as req:
        req.write("\n".join(requirements))

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv"
    }

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "pip",
        "install", "-r", ".torque/local/requirements.txt",
        "--upgrade"
    ]

    try:
        subprocess.run(cmd, cwd=v1.utils.torque_root(), env=env, check=True)

    except subprocess.CalledProcessError as exc:
        raise exceptions.ExecuteFailed("pip") from exc


def install_package(uri: str):
    """TODO"""

    if re.match(_URI, uri) is None and os.path.exists(uri):
        if not os.path.isabs(uri):
            uri = os.path.join(v1.utils.torque_cwd(), uri)
            uri = os.path.normpath(uri)

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv"
    }

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "pip",
        "install"
    ]

    cmd += [
        "-t", ".torque/system",
        "--platform", "torque",
        "--implementation", "py3",
        "--no-deps",
        "--no-index",
        uri
    ]

    try:
        subprocess.run(cmd, cwd=v1.utils.torque_root(), env=env, check=True)

    except subprocess.CalledProcessError as exc:
        raise exceptions.ExecuteFailed("pip") from exc


def remove_package(name: str):
    """TODO"""

    packages = installed_packages()

    if name not in packages:
        raise exceptions.PackageNotFound(name)

    dist = metadata.Distribution.at(packages[name]["path"])
    files = set()

    for file in dist.files:
        for i in range(len(file.parts)):
            files.add(os.path.join(*file.parts[:i+1]))

    for file in sorted(files, reverse=True):
        path = f"{v1.utils.torque_dir()}/system/{file}"

        try:
            if os.path.isdir(path):
                os.rmdir(path)

            else:
                os.unlink(path)

        except FileNotFoundError:
            pass

        except OSError as exc:
            if exc.errno != 39:
                raise


def list_packages():
    """TODO"""

    for name, metadata in installed_packages().items():
        print(f"{name}: version: {metadata['version']}, uri: {metadata['uri']}", file=sys.stdout)


def upgrade_package(name: str):
    """TODO"""

    packages = installed_packages()

    if name not in packages:
        raise exceptions.PackageNotFound(name)

    remove_package(name)
    install_package(packages[name]["uri"])

    install_deps()


def upgrade_all_packages():
    """TODO"""

    for name, metadata in installed_packages().items():
        remove_package(name)
        install_package(metadata["uri"])

    install_deps()
