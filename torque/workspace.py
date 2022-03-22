# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import sys

from importlib import metadata


def initialize_venv(target: str):
    """TODO"""

    subprocess.run([sys.executable,
                    "-m", "venv",
                    "--prompt", "torque",
                    f"{target}/.torque/local/venv"],
                   env=os.environ,
                   check=True)

    os.chdir(target)

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv",
    }

    try:
        subprocess.run([".torque/local/venv/bin/python",
                        "-m", "pip",
                        "install", "-U",
                        "pip", "wheel", "setuptools"],
                       env=env,
                       check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install venv") from exc

    with open(".torque/local/install_deps", "w", encoding="utf8"):
        pass


def install_torque(package: str):
    """TODO"""

    env = os.environ | {
        "PYTHONPATH": ".torque/system"
    }

    cmd = [
        sys.executable,
        "-m", "pip",
        "install",
        "-t", ".torque/system",
        "--platform", "torque",
        "--implementation", "py3",
        "--no-deps",
        "--no-index"
    ]

    cmd += [package]

    try:
        subprocess.run(cmd, env=env, check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install torque-workspace package") from exc


def install_deps():
    """TODO"""

    requires = []

    for entry in os.listdir(".torque/system"):
        if not entry.endswith(".dist-info"):
            continue

        dist = metadata.Distribution.at(f".torque/system/{entry}")
        dist_requires = dist.metadata.get_all("Requires-Dist")

        if dist_requires:
            requires += dist_requires

    if os.path.isfile(".torque/requires.txt"):
        with open(".torque/requires.txt", encoding="utf8") as file:
            requires += [i.strip() for i in file]

    with open(".torque/local/requires.txt", "w", encoding="utf8") as req:
        req.write("\n".join(requires))

    requires += [""]

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv"
    }

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "pip",
        "install", "-r", ".torque/local/requires.txt",
        "--force-reinstall", "--upgrade"
    ]

    subprocess.run(cmd, env=env, check=True)
    os.unlink(".torque/local/install_deps")
