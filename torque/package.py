# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re
import subprocess
import sys

from importlib import metadata

from torque import exceptions
from torque import utils


_URI = r"^[^:]+://"


def install_deps(force: bool, upgrade: bool):
    """TODO"""

    torque_dir = f"{utils.torque_root()}/.torque"
    requirements = []

    for entry in os.listdir(f"{torque_dir}/system"):
        if not entry.endswith(".dist-info"):
            continue

        dist = metadata.Distribution.at(f"{torque_dir}/system/{entry}")
        dist_requires = dist.metadata.get_all("Requires-Dist")

        if dist_requires:
            requirements += dist_requires

    if os.path.isfile(f"{torque_dir}/requirements.txt"):
        with open(f"{torque_dir}/requirements.txt", encoding="utf8") as file:
            requirements += [i.strip() for i in file]

    requirements += [""]

    with open(f"{torque_dir}/local/requirements.txt", "w", encoding="utf8") as req:
        req.write("\n".join(requirements))

    env = os.environ | {
        "VIRTUAL_ENV": f"{torque_dir}/local/venv"
    }

    cmd = [
        f"{torque_dir}/local/venv/bin/python",
        "-m", "pip",
        "install", "-r", f"{torque_dir}/local/requirements.txt"
    ]

    if force:
        cmd += ["--force-reinstall"]

    if upgrade:
        cmd += ["--upgrade"]

    try:
        subprocess.run(cmd, env=env, check=True)

    except subprocess.CalledProcessError as exc:
        raise exceptions.ExecuteFailed("pip") from exc


def install_package(package: str, force: bool, upgrade: bool):
    """TODO"""

    torque_dir = f"{utils.torque_root()}/.torque"

    if re.match(_URI, package) is None and os.path.exists(package):
        if not os.path.isabs(package):
            package = os.path.join(utils.torque_cwd(), package)
            package = os.path.normpath(package)

    env = os.environ | {
        "VIRTUAL_ENV": f"{torque_dir}/local/venv"
    }

    cmd = [
        f"{torque_dir}/local/venv/bin/python",
        "-m", "pip",
        "install"
    ]

    if force:
        cmd += ["--force-reinstall"]

    if upgrade:
        cmd += ["--upgrade"]

    cmd += [
        "-t", f"{torque_dir}/system",
        "--platform", "torque",
        "--implementation", "py3",
        "--no-deps",
        "--no-index",
        package
    ]

    try:
        subprocess.run(cmd, env=env, check=True)

    except subprocess.CalledProcessError as exc:
        raise exceptions.ExecuteFailed("pip") from exc

    install_deps(force, upgrade)


def remove_package(package: str, used_component_types: set[str], used_link_types: set[str]):
    """TODO"""

    torque_dir = f"{utils.torque_root()}/.torque"
    dist = metadata.Distribution.at(f"{torque_dir}/system/{package}.dist-info")

    if not dist.files:
        raise exceptions.PackageNotFound(package)

    component_types = filter(lambda x: x.group == "torque.components.v1", dist.entry_points)
    component_types = {i.name for i in list(component_types)}

    if len(component_types & used_component_types) != 0:
        raise exceptions.PackageInUse(package)

    link_types = filter(lambda x: x.group == "torque.links.v1", dist.entry_points)
    link_types = {i.name for i in list(link_types)}

    if len(link_types & used_link_types) != 0:
        raise exceptions.PackageInUse(package)

    files = set()

    for file in dist.files:
        for i in range(len(file.parts)):
            files.add(os.path.join(*file.parts[:i+1]))

    for file in sorted(files, reverse=True):
        path = f"{torque_dir}/system/{file}"

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

    torque_dir = f"{utils.torque_root()}/.torque"

    for entry in os.listdir(f"{torque_dir}/system"):
        if not entry.endswith(".dist-info"):
            continue

        package = entry.removesuffix(".dist-info")
        print(f"{package}", file=sys.stdout)
