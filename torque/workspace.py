# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import sys

from importlib import metadata


def initialize_venv(root: str):
    """TODO"""

    torque_dir = f"{root}/.torque"

    subprocess.run([sys.executable,
                    "-m", "venv",
                    "--prompt", "torque",
                    "--clear",
                    "--upgrade-deps",
                    f"{torque_dir}/local/venv"],
                   env=os.environ,
                   check=True)

    env = os.environ | {
        "VIRTUAL_ENV": f"{torque_dir}/local/venv",
    }

    try:
        subprocess.run([f"{torque_dir}/local/venv/bin/python",
                        "-m", "pip",
                        "install", "-U",
                        "wheel"],
                       env=env,
                       check=True)

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to install venv") from exc

    try:
        p = subprocess.run([f"{torque_dir}/local/venv/bin/python",
                            "-c", "import site; print(site.getsitepackages()[0])"],
                           env=env,
                           check=True,
                           capture_output=True)

        site_packages = p.stdout.decode('utf8')
        site_packages = site_packages.strip()

    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to get site-packages directory") from exc

    with open(f"{site_packages}/torque.pth", "a", encoding="utf8") as file:
        print(f"{torque_dir}/system", file=file)
        print(f"{torque_dir}/site", file=file)

    with open(f"{torque_dir}/local/install_deps", "w", encoding="utf8"):
        pass


def install_torque(root: str, package: str):
    """TODO"""

    torque_dir = f"{root}/.torque"

    cmd = [
        sys.executable,
        "-m", "pip",
        "install",
        "-t", f"{torque_dir}/system",
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


def install_deps(root: str):
    """TODO"""

    torque_dir = f"{root}/.torque"
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
        "install", "-r", f"{torque_dir}/local/requirements.txt",
        "--force-reinstall", "--upgrade"
    ]

    subprocess.run(cmd, env=env, check=True)
    os.unlink(f"{torque_dir}/local/install_deps")
