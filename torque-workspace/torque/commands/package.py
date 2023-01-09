# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import sys

import yaml

from torque import package
from torque import repository


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

    yaml.safe_dump(sorted(list(package.installed_packages())),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _describe(arguments: argparse.Namespace):
    """DOCSTRING"""

    desc = package.describe_package(arguments.name)
    repo = repository.package_repository(arguments.name)

    repo = repo["v1"]

    desc.update({
        "contexts": sorted(list(repo["contexts"])),
        "components": sorted(list(repo["components"])),
        "links": sorted(list(repo["links"])),
        "providers": sorted(list(repo["providers"])),
        "bonds": sorted(list(repo["bonds"]))
    })

    yaml.safe_dump(desc,
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


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

    describe_parser = subparsers.add_parser("describe", help="describe package")
    describe_parser.add_argument("name", help="package name")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """DOCSTRING"""

    cmds = {
        "install": _install,
        "uninstall": _uninstall,
        "upgrade": _upgrade,
        "upgrade-all": _upgrade_all,
        "list": _list,
        "describe": _describe
    }

    cmds[arguments.package_cmd](arguments)
