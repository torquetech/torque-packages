# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import exceptions
from torque import layout
from torque import package


def _install(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    package.install_package(arguments.package, arguments.force, arguments.upgrade)


def _remove(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        package.remove_package(arguments.package,
                               _layout.dag.used_component_types(),
                               _layout.dag.used_link_types())

    except exceptions.PackageNotFound as exc:
        raise RuntimeError(f"{arguments.package}: package not found") from exc

    except exceptions.PackageInUse as exc:
        raise RuntimeError(f"{arguments.package}: package in use") from exc


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    package.list_packages()


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("package",
                                   description="package management",
                                   help="package management")

    subparsers = parser.add_subparsers(required=True, dest="package_cmd", metavar="command")

    install_parser = subparsers.add_parser("install",
                                           description="install package",
                                           help="install package")

    install_parser.add_argument("--upgrade", "-u",
                                action="store_true",
                                help="upgrade package")

    install_parser.add_argument("--force", "-f",
                                action="store_true",
                                help="force install")

    install_parser.add_argument("package", help="package to install")

    remove_parser = subparsers.add_parser("remove",
                                          description="remove package",
                                          help="remove package")

    remove_parser.add_argument("package", help="package to remove")

    subparsers.add_parser("list",
                          description="list installed packages",
                          help="list installed packages")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "install": _install,
        "remove": _remove,
        "list": _list
    }

    cmds[arguments.package_cmd](arguments)
