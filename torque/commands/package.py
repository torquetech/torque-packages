# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import exceptions
from torque import workspace
from torque import package


def _install(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    package.install_package(arguments.uri, arguments.upgrade)


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        package.remove_package(arguments.name,
                               ws.dag.used_component_types(),
                               ws.dag.used_link_types())

    except exceptions.PackageNotFound as exc:
        raise RuntimeError(f"{exc}: package not found") from exc

    except exceptions.PackageInUse as exc:
        raise RuntimeError(f"{exc}: package in use") from exc


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    package.list_packages()


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("package", help="package management")
    subparsers = parser.add_subparsers(required=True, dest="package_cmd", metavar="command")

    install_parser = subparsers.add_parser("install", help="install package")
    install_parser.add_argument("--upgrade", action="store_true", help="upgrade package")
    install_parser.add_argument("uri", help="package uri")

    remove_parser = subparsers.add_parser("remove", help="remove package")
    remove_parser.add_argument("name", help="package name")

    subparsers.add_parser("list", help="list installed packages")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "install": _install,
        "remove": _remove,
        "list": _list
    }

    cmds[arguments.package_cmd](arguments)
