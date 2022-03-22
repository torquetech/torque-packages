# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


import argparse


def _create(arguments: argparse.Namespace):
    """TODO"""


def _remove(arguments: argparse.Namespace):
    """TODO"""


def _show(arguments: argparse.Namespace):
    """TODO"""


def _list(arguments: argparse.Namespace):
    """TODO"""


def _build(arguments: argparse.Namespace):
    """TODO"""


def _apply(arguments: argparse.Namespace):
    """TODO"""


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("deployment", help="deployment management")
    subparsers = parser.add_subparsers(required=True, dest="deployment_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create deployment")
    create_parser.add_argument("--groups", help="groups to use")
    create_parser.add_argument("--components", help="components to use")
    create_parser.add_argument("name", help="deployment name")
    create_parser.add_argument("profile", help="profile to use")

    remove_parser = subparsers.add_parser("remove", help="remove deployment")
    remove_parser.add_argument("name", help="deployment name")

    show_parser = subparsers.add_parser("show", help="show deployment")
    show_parser.add_argument("name", help="deployment name")

    list_parser = subparsers.add_parser("list", help="list deployments")

    build_parser = subparsers.add_parser("build", help="build deployment")
    build_parser.add_argument("name", help="deployment name")

    apply_parser = subparsers.add_parser("apply", help="apply deployment")
    apply_parser.add_argument("name", help="deployment name")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "build": _build,
        "apply": _apply
    }

    cmds[arguments.deployment_cmd](arguments)
