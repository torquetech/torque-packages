# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


_URI = r"^[^:]+://"


def initialize_venv(root: str):
    """DOCSTRING"""

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


def install_torque(root: str, uri: str):
    """DOCSTRING"""

    if re.match(_URI, uri) is None and os.path.exists(uri):
        if not os.path.isabs(uri):
            uri = os.path.join(torque_cwd(), uri)
            uri = os.path.normpath(uri)

    torque_dir = f"{root}/.torque"
    tmp = tempfile.mkdtemp()

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv"
    }

    try:
        subprocess.run([sys.executable,
                        "-m", "pip", "wheel",
                        "--wheel-dir", tmp,
                        "--no-deps",
                        "--no-index",
                        uri
                        ],
                       cwd=root,
                       env=env,
                       check=True)

        files = os.listdir(tmp)

        for file in files:
            if not file.endswith("-py3-none-torque.whl"):
                continue

            with zipfile.ZipFile(f"{tmp}/{file}") as whl:
                for item in whl.infolist():
                    path = whl.extract(item, f"{torque_dir}/system")

                    if item.create_system == 3:
                        attrs = item.external_attr >> 16
                        os.chmod(path, attrs)

            package = file.replace("-py3-none-torque.whl", ".dist-info")

            direct_url = f"{torque_dir}/system/{package}/direct_url.json"
            with open(direct_url, "w", encoding="utf-8") as file:
                file.write(json.dumps({
                    "dir_info": {},
                    "url": uri
                }))

            record = f"{torque_dir}/system/{package}/RECORD"
            with open(record, "a", encoding="utf-8") as file:
                file.write(f"{package}/direct_url.json,,\n")

    finally:
        shutil.rmtree(tmp)


def install_deps(root: str):
    """DOCSTRING"""

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "torque.hooks.install_deps"
    ]

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv",
        "PWD": root
    }

    subprocess.run(cmd, cwd=root, env=env, check=True)
