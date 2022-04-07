# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re

from argparse import Namespace

from torque import workspace


_URI = r"^[^:]+://"


def add_arguments(subparsers):
    """TODO"""

    init_parser = subparsers.add_parser("init",
                                        description="initialize workspace",
                                        help="initialize workspace")

    init_parser.add_argument("--package",
                             metavar="package",
                             default="git+https://github.com/torquetech/torque-workspace@stable",
                             help="torque-workspace package to install, default: %(default)s")
    init_parser.add_argument("--no-package",
                             action="store_true",
                             help="skip installing of torque-workspace package")

    init_parser.add_argument("path", help="path to initialize torque in")


def run(arguments: Namespace):
    """TODO"""

    package = arguments.package

    if re.match(_URI, package) is None and os.path.exists(package):
        package = os.path.abspath(arguments.package)

    if os.path.exists(f"{arguments.path}/.torque"):
        raise RuntimeError(f"{arguments.path}: already has .torque directory")

    os.makedirs(f"{arguments.path}/.torque/system")
    os.chdir(f"{arguments.path}")

    if not arguments.no_package:
        workspace.install_torque(package)

    with open(".torque/.gitignore", "w", encoding="utf8") as file:
        print("local", file=file)
        print("**/__pycache__", file=file)
