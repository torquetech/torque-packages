# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import sys


def initialize_venv(target: str):
    """TODO"""

    subprocess.run([sys.executable,
                    "-m", "venv",
                    "--prompt", "torque",
                    f"{target}/.torque/cache/venv"],
                   check=True)

    os.chdir(target)

    env = {
        "VIRTUAL_ENV": ".torque/cache/venv",
    }

    try:
        subprocess.run([".torque/cache/venv/bin/python",
                        "-m", "pip",
                        "install", "-U",
                        "pip", "wheel", "setuptools"],
                       env=env,
                       check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install venv") from exc

    with open(".torque/cache/install_deps", "w", encoding="utf8"):
        pass


def install_torque(package: str):
    """TODO"""

    env = {
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
