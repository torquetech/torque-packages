# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse

from torque import package


def _install(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    package.install_package(arguments.uri)
    package.install_deps()


def _uninstall(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    package.uninstall_package(arguments.name)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    package.list_packages()


def _upgrade(arguments: argparse.Namespace):
    """DOCSTRING"""

    package.upgrade_package(arguments.name)


def _upgrade_all(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    package.upgrade_all_packages()


def add_arguments(subparsers):
    """DOCSTRING"""

    parser = subparsers.add_parser("package", help="package management")
    subparsers = parser.add_subparsers(required=True, dest="package_cmd", metavar="command")

    install_parser = subparsers.add_parser("install", help="install package")
    install_parser.add_argument("uri", help="package uri")

    uninstall_parser = subparsers.add_parser("uninstall", help="uninstall package")
    uninstall_parser.add_argument("name", help="package name")

    upgrade_parser = subparsers.add_parser("upgrade", help="upgrade package")
    upgrade_parser.add_argument("name", help="upgrade package")

    subparsers.add_parser("upgrade-all", help="upgrade all packages")
    subparsers.add_parser("list", help="list installed packages")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """DOCSTRING"""

    cmds = {
        "install": _install,
        "uninstall": _uninstall,
        "upgrade": _upgrade,
        "upgrade-all": _upgrade_all,
        "list": _list
    }

    cmds[arguments.package_cmd](arguments)
