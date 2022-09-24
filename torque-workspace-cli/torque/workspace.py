# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import sys


def initialize_venv(root: str):
    """TODO"""

    subprocess.run([sys.executable,
                    "-m", "venv",
                    "--prompt", "torque",
                    "--clear",
                    "--upgrade-deps",
                    ".torque/local/venv"],
                   cwd=root,
                   env=os.environ,
                   check=True)

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv",
    }

    try:
        subprocess.run([".torque/local/venv/bin/python",
                        "-m", "pip",
                        "install", "-U",
                        "wheel"],
                       cwd=root,
                       env=env,
                       check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install venv") from exc

    try:
        p = subprocess.run([".torque/local/venv/bin/python",
                            "-c", "import site; print(site.getsitepackages()[0])"],
                           cwd=root,
                           env=env,
                           check=True,
                           capture_output=True)

        site_packages = p.stdout.decode("utf8")
        site_packages = site_packages.strip()

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to get site-packages directory") from exc

    with open(f"{site_packages}/torque.pth", "a", encoding="utf8") as file:
        print(os.path.relpath(f"{root}/.torque/system", site_packages), file=file)
        print(os.path.relpath(f"{root}/.torque/site", site_packages), file=file)


def install_torque(root: str, package: str):
    """TODO"""

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
        subprocess.run(cmd, cwd=root, env=os.environ, check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install torque-workspace package") from exc


def install_deps(root: str):
    """TODO"""

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "torque.hooks.install_deps"
    ]

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv",
        "PWD": root
    }

    subprocess.run(cmd, cwd=root, env=env, check=True)
