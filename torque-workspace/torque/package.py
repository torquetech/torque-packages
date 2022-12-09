# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import zipfile

from importlib import metadata


_URI = r"^[^:]+://"
_TORQUE_CWD = None
_TORQUE_ROOT = None


class Exception(RuntimeError):
    """TODO"""


class PackageNotFound(Exception):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: package not found"


class WorkspaceNotFound(Exception):
    """TODO"""

    def __str__(self) -> str:
        return "workspace not found!"


def torque_cwd() -> str:
    # pylint: disable=W0603

    """TODO"""

    global _TORQUE_CWD

    if _TORQUE_CWD:
        return _TORQUE_CWD

    _TORQUE_CWD = os.getenv("PWD", os.getcwd())

    return _TORQUE_CWD


def torque_root() -> str:
    # pylint: disable=W0603

    """TODO"""

    global _TORQUE_ROOT

    if _TORQUE_ROOT:
        return _TORQUE_ROOT

    cwd = pathlib.Path(torque_cwd())

    while True:
        if os.path.isdir(f"{cwd}/.torque"):
            break

        if cwd.parent == cwd:
            raise WorkspaceNotFound()

        cwd = cwd.parent

    _TORQUE_ROOT = str(cwd)

    return _TORQUE_ROOT


def torque_dir() -> str:
    """TODO"""

    return f"{torque_root()}/.torque"


def package_dist(path: str):
    """TODO"""

    return metadata.Distribution.at(path)


def installed_packages():
    """TODO"""

    packages = {}

    for entry in os.listdir(f"{torque_dir()}/system"):
        if not entry.endswith(".dist-info"):
            continue

        path = f"{torque_dir()}/system/{entry}"
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

    if os.path.isfile(f"{torque_dir()}/requirements.txt"):
        with open(f"{torque_dir()}/requirements.txt", encoding="utf8") as file:
            requirements += [i.strip() for i in file]

    requirements += [""]

    with open(f"{torque_dir()}/local/requirements.txt", "w", encoding="utf8") as req:
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

    subprocess.run(cmd, cwd=torque_root(), env=env, check=True)


def install_package(uri: str):
    """TODO"""

    if re.match(_URI, uri) is None and os.path.exists(uri):
        if not os.path.isabs(uri):
            uri = os.path.join(torque_cwd(), uri)
            uri = os.path.normpath(uri)

    tmp = tempfile.mkdtemp()

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv"
    }

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "pip", "wheel",
        "--wheel-dir", tmp,
        "--no-deps",
        "--no-index",
        uri
    ]

    try:
        subprocess.run(cmd, cwd=torque_root(), env=env, check=True)

        files = os.listdir(tmp)

        for file in files:
            if not file.endswith("-py3-none-torque.whl"):
                continue

            with zipfile.ZipFile(f"{tmp}/{file}") as whl:
                for item in whl.infolist():
                    path = whl.extract(item, f"{torque_dir()}/system")

                    if item.create_system == 3:
                        attrs = item.external_attr >> 16
                        os.chmod(path, attrs)

            package = file.replace("-py3-none-torque.whl", ".dist-info")

            direct_url = f"{torque_dir()}/system/{package}/direct_url.json"
            with open(direct_url, "w", encoding="utf-8") as file:
                file.write(json.dumps({
                    "dir_info": {},
                    "url": uri
                }))

            record = f"{torque_dir()}/system/{package}/RECORD"
            with open(record, "a", encoding="utf-8") as file:
                file.write(f"{package}/direct_url.json,,\n")

    finally:
        shutil.rmtree(tmp)


def uninstall_package(name: str):
    """TODO"""

    packages = installed_packages()

    if name not in packages:
        raise PackageNotFound(name)

    dist = metadata.Distribution.at(packages[name]["path"])
    files = set()

    for file in dist.files:
        for i in range(len(file.parts)):
            files.add(os.path.join(*file.parts[:i+1]))

    for file in sorted(files, reverse=True):
        path = f"{torque_dir()}/system/{file}"

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

    for name, metadata in sorted(installed_packages().items()):
        print(f"{name}: version: {metadata['version']}, uri: {metadata['uri']}")


def upgrade_package(name: str):
    """TODO"""

    packages = installed_packages()

    if name not in packages:
        raise PackageNotFound(name)

    uninstall_package(name)
    install_package(packages[name]["uri"])

    install_deps()


def upgrade_all_packages():
    """TODO"""

    for name, metadata in installed_packages().items():
        uninstall_package(name)
        install_package(metadata["uri"])

    install_deps()
