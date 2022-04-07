# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import sys

from importlib import metadata


def initialize_venv():
    """TODO"""

    subprocess.run([sys.executable,
                    "-m", "venv",
                    "--prompt", "torque",
                    "--clear",
                    "--upgrade-deps",
                    f".torque/local/venv"],
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
                       env=env,
                       check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install venv") from exc

    try:
        p = subprocess.run([".torque/local/venv/bin/python",
                            "-c", "import site; print(site.getsitepackages()[0])"],
                           env=env,
                           check=True,
                           capture_output=True)

        site_packages = p.stdout.decode('utf8')
        site_packages = site_packages.strip()

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to get site-packages directory") from exc

    with open(f"{site_packages}/torque.pth", "a", encoding="utf8") as file:
        print(f"{os.getcwd()}/.torque/system", file=file)
        print(f"{os.getcwd()}/.torque/site", file=file)

    with open(".torque/local/install_deps", "w", encoding="utf8"):
        pass


def install_torque(package: str):
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
        subprocess.run(cmd, env=os.environ, check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install torque-workspace package") from exc


def install_deps():
    """TODO"""

    requirements = []

    for entry in os.listdir(".torque/system"):
        if not entry.endswith(".dist-info"):
            continue

        dist = metadata.Distribution.at(f".torque/system/{entry}")
        dist_requires = dist.metadata.get_all("Requires-Dist")

        if dist_requires:
            requirements += dist_requires

    if os.path.isfile(".torque/requirements.txt"):
        with open(".torque/requirements.txt", encoding="utf8") as file:
            requirements += [i.strip() for i in file]

    requirements += [""]

    with open(".torque/local/requirements.txt", "w", encoding="utf8") as req:
        req.write("\n".join(requirements))

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv"
    }

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "pip",
        "install", "-r", ".torque/local/requirements.txt",
        "--force-reinstall", "--upgrade"
    ]

    subprocess.run(cmd, env=env, check=True)
    os.unlink(".torque/local/install_deps")
