# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os
import re

from argparse import Namespace

from torque import workspace


_URI = r"^[^:]+://"


def add_arguments(subparsers):
    """DOCSTRING"""

    init_parser = subparsers.add_parser("init",
                                        description="initialize workspace",
                                        help="initialize workspace")

    init_parser.add_argument("--package",
                             metavar="package",
                             default="git+https://github.com/torquetech/torque-workspace",
                             help="torque-workspace package to install, default: %(default)s")
    init_parser.add_argument("--no-package",
                             action="store_true",
                             help="skip installing of torque-workspace package")

    init_parser.add_argument("path", help="path to initialize torque in")


def run(cwd: str, arguments: Namespace):
    """DOCSTRING"""

    package = arguments.package

    if re.match(_URI, package) is None and os.path.exists(package):
        if not os.path.isabs(package):
            package = os.path.join(cwd, package)
            package = os.path.normpath(package)

    root = arguments.path

    if not os.path.isabs(root):
        root = os.path.join(cwd, root)
        root = os.path.normpath(root)

    if os.path.exists(f"{root}/.torque"):
        raise RuntimeError(f"{root}: already has .torque directory")

    os.makedirs(f"{root}/.torque/system")

    if not arguments.no_package:
        workspace.install_torque(root, package)

    with open(f"{root}/.torque/.gitignore", "w", encoding="utf8") as file:
        print("local", file=file)
        print("**/__pycache__", file=file)

    workspace.initialize_venv(root)

    if not arguments.no_package:
        workspace.install_deps(root)
