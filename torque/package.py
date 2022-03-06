# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re
import subprocess

from importlib import metadata


_URI = r"^[^:]+://"


def install_deps(force: bool, upgrade: bool):
    """TODO"""

    requires = []

    for entry in os.listdir(".torque/system"):
        if not entry.endswith(".dist-info"):
            continue

        dist = metadata.Distribution.at(f".torque/system/{entry}")
        dist_requires = dist.metadata.get_all("Requires-Dist")

        if dist_requires:
            requires += dist_requires

    with open(".torque/cache/requires.txt", "w", encoding="utf8") as req:
        req.write("\n".join(requires))

    env = {
        "VIRTUAL_ENV": ".torque/cache/venv"
    }

    cmd = [
        ".torque/cache/venv/bin/python",
        "-m", "pip",
        "install", "-r", ".torque/cache/requires.txt"
    ]

    if force:
        cmd += ["--force-reinstall"]

    if upgrade:
        cmd += ["--upgrade"]

    subprocess.run(cmd, env=env, check=True)

    try:
        os.unlink(".torque/cache/install_deps")

    except FileNotFoundError:
        pass


def install_package(package: str, force: bool, upgrade: bool):
    """TODO"""

    if re.match(_URI, package) is None and os.path.exists(package):
        package = os.path.abspath(package)

    env = {
        "VIRTUAL_ENV": ".torque/cache/venv",
        "PYTHONPATH": ".torque/system"
    }

    cmd = [
        ".torque/cache/venv/bin/python",
        "-m", "pip",
        "install"
    ]

    if force:
        cmd += ["--force-reinstall"]

    if upgrade:
        cmd += ["--upgrade"]

    cmd += [
        "-t", ".torque/system",
        "--platform", "torque",
        "--implementation", "py3",
        "--no-deps",
        "--no-index",
        package
    ]

    subprocess.run(cmd, env=env, check=True)

    install_deps(force, upgrade)


def remove_package(package: str, used_component_types: set[str], used_link_types: set[str]):
    """TODO"""

    dist = metadata.Distribution.at(f".torque/system/{package}.dist-info")

    if not dist.files:
        raise RuntimeError(f"{package}: package not found")

    component_types = list(filter(lambda x: x.group == "torque.components", dist.entry_points))
    component_types = {i.name for i in component_types}

    if len(component_types & used_component_types) != 0:
        raise RuntimeError(f"{package}: package in use")

    link_types = list(filter(lambda x: x.group == "torque.links", dist.entry_points))
    link_types = {i.name for i in link_types}

    if len(link_types & used_link_types) != 0:
        raise RuntimeError(f"{package}: package in use")

    files = set()

    for file in dist.files:
        for i in range(len(file.parts)):
            files.add(os.path.join(*file.parts[:i+1]))

    for file in sorted(files, reverse=True):
        path = f".torque/system/{file}"

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

    for entry in os.listdir(".torque/system"):
        if not entry.endswith(".dist-info"):
            continue

        package = entry.removesuffix(".dist-info")
        print(f"{package}")
