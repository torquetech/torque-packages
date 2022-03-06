# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import configuration

from torque.package import install_package, remove_package, list_packages


def _install(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    install_package(arguments.package, arguments.force, arguments.upgrade)


def _remove(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    used_component_types = {i.type for i in config["components"].values()}
    used_link_types = {i.type for i in config["links"].values()}

    remove_package(arguments.package, used_component_types, used_link_types)


def _list(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    list_packages()


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

    config = configuration.load(arguments.config)

    cmd = {
        "install": _install,
        "remove": _remove,
        "list": _list
    }

    cmd[arguments.package_cmd](arguments, config)
