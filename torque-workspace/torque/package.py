# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import importlib.metadata
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import zipfile


_URI = r"^[^:]+://"
_TORQUE_CWD = None
_TORQUE_ROOT = None


class Exception(RuntimeError):
    """DOCSTRING"""


class PackageNotFound(Exception):
    """DOCSTRING"""

    def __str__(self) -> str:
        return f"{self.args[0]}: package not found"


class WorkspaceNotFound(Exception):
    """DOCSTRING"""

    def __str__(self) -> str:
        return "workspace not found!"


def _torque_cwd() -> str:
    # pylint: disable=W0603

    """DOCSTRING"""

    global _TORQUE_CWD

    if _TORQUE_CWD:
        return _TORQUE_CWD

    _TORQUE_CWD = os.getenv("PWD", os.getcwd())

    return _TORQUE_CWD


def _torque_root() -> str:
    # pylint: disable=W0603

    """DOCSTRING"""

    global _TORQUE_ROOT

    if _TORQUE_ROOT:
        return _TORQUE_ROOT

    cwd = pathlib.Path(_torque_cwd())

    while True:
        if os.path.isdir(f"{cwd}/.torque"):
            break

        if cwd.parent == cwd:
            raise WorkspaceNotFound()

        cwd = cwd.parent

    _TORQUE_ROOT = str(cwd)

    return _TORQUE_ROOT


def _torque_dir() -> str:
    """DOCSTRING"""

    return f"{_torque_root()}/.torque"


def _package_dist(path: str):
    """DOCSTRING"""

    return importlib.metadata.Distribution.at(path)


def installed_packages():
    """DOCSTRING"""

    packages = {}

    for entry in os.listdir(f"{_torque_dir()}/system"):
        if not entry.endswith(".dist-info"):
            continue

        path = f"{_torque_dir()}/system/{entry}"
        dist = _package_dist(path)

        with open(f"{path}/direct_url.json", encoding="utf-8") as f:
            uri = json.loads(f.read())["url"]

        packages[dist.name] = {
            "version": dist.metadata["Version"],
            "path": path,
            "uri": uri
        }

    return packages


def install_deps():
    """DOCSTRING"""

    requirements = []

    for metadata in installed_packages().values():
        dist = _package_dist(metadata["path"])
        dist_requires = dist.metadata.get_all("Requires-Dist")

        if dist_requires:
            requirements += dist_requires

    if os.path.isfile(f"{_torque_dir()}/requirements.txt"):
        with open(f"{_torque_dir()}/requirements.txt", encoding="utf8") as file:
            requirements += [i.strip() for i in file]

    requirements += [""]

    with open(f"{_torque_dir()}/local/requirements.txt", "w", encoding="utf8") as req:
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

    subprocess.run(cmd, cwd=_torque_root(), env=env, check=True)


def install_package(uri: str):
    """DOCSTRING"""

    if re.match(_URI, uri) is None and os.path.exists(uri):
        if not os.path.isabs(uri):
            uri = os.path.join(_torque_cwd(), uri)
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
        subprocess.run(cmd, cwd=_torque_root(), env=env, check=True)

        files = os.listdir(tmp)

        for file in files:
            if not file.endswith("-py3-none-torque.whl"):
                continue

            with zipfile.ZipFile(f"{tmp}/{file}") as whl:
                for item in whl.infolist():
                    path = whl.extract(item, f"{_torque_dir()}/system")

                    if item.create_system == 3:
                        attrs = item.external_attr >> 16
                        os.chmod(path, attrs)

            package = file.replace("-py3-none-torque.whl", ".dist-info")

            direct_url = f"{_torque_dir()}/system/{package}/direct_url.json"
            with open(direct_url, "w", encoding="utf-8") as file:
                file.write(json.dumps({
                    "dir_info": {},
                    "url": uri
                }))

            record = f"{_torque_dir()}/system/{package}/RECORD"
            with open(record, "a", encoding="utf-8") as file:
                file.write(f"{package}/direct_url.json,,\n")

    finally:
        shutil.rmtree(tmp)


def uninstall_package(name: str):
    """DOCSTRING"""

    packages = installed_packages()

    if name not in packages:
        raise PackageNotFound(name)

    dist = importlib.metadata.Distribution.at(packages[name]["path"])
    files = set()

    for file in dist.files:
        for i in range(len(file.parts)):
            files.add(os.path.join(*file.parts[:i+1]))

    for file in sorted(files, reverse=True):
        path = f"{_torque_dir()}/system/{file}"

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


def upgrade_package(name: str):
    """DOCSTRING"""

    packages = installed_packages()

    if name not in packages:
        raise PackageNotFound(name)

    uninstall_package(name)
    install_package(packages[name]["uri"])

    install_deps()


def upgrade_all_packages():
    """DOCSTRING"""

    for name, metadata in installed_packages().items():
        uninstall_package(name)
        install_package(metadata["uri"])

    install_deps()


def describe_package(name: str) -> dict[str, object]:
    """DOCSTRING"""

    packages = installed_packages()

    if name not in packages:
        raise PackageNotFound(name)

    package = packages[name]

    dist = _package_dist(package["path"])
    metadata = dist.metadata

    return {
        "name": metadata["Name"],
        "version": metadata["Version"],
        "home-page": metadata["Home-page"],
        "author": metadata["Author"],
        "author-email": metadata["Author-email"],
        "license": metadata["License"],
        "uri": package["uri"]
    }
