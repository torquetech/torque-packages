# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import sys

from torque import v1
from torque import workspace


def _create(arguments: argparse.Namespace):
    """TODO"""

    params = workspace.process_parameters(arguments.params_file, arguments.params)
    ws = workspace.load(arguments.workspace)

    if arguments.no_suffix and not arguments.name:
        raise v1.exceptions.RuntimeError("if --no-suffix is specified, name must be supplied")

    ws.create_link(arguments.name,
                   arguments.type,
                   params,
                   arguments.source,
                   arguments.destination,
                   arguments.no_suffix)
    ws.store()


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    ws.remove_link(arguments.name)
    ws.store()


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)
    link = ws.get_link(arguments.name)

    print(f"{link}", file=sys.stdout)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)

    for link in ws.dag.links.values():
        print(f"{link}", file=sys.stdout)


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    link_type = ws.repo.link(arguments.name)
    print(f"{arguments.name}: {link_type}", file=sys.stdout)


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)
    link_types = ws.repo.links()

    for link in link_types:
        print(f"{link}: {link_types[link]}", file=sys.stdout)


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("link", help="link management")
    subparsers = parser.add_subparsers(required=True, dest="link_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create link")
    create_parser.add_argument("--params-file", help="link parameters file")
    create_parser.add_argument("--param", "-p",
                               action="append",
                               metavar="NAME=VALUE",
                               dest="params",
                               help="link parameter")
    create_parser.add_argument("--no-suffix",
                               action="store_true",
                               help="don't append unique suffix to the name")
    create_parser.add_argument("--name", help="link name")
    create_parser.add_argument("--type",
                               default="torque.defaults.V1DependencyLink",
                               help="link type, default: %(default)s")
    create_parser.add_argument("source", help="source component")
    create_parser.add_argument("destination", help="destination component")

    remove_parser = subparsers.add_parser("remove", help="remove link")
    remove_parser.add_argument("name", help="link name")

    show_parser = subparsers.add_parser("show", help="show link")
    show_parser.add_argument("name", help="link name")

    subparsers.add_parser("list", help="list links")

    show_type_parser = subparsers.add_parser("show-type", help="show link type")
    show_type_parser.add_argument("name", help="link type name")

    subparsers.add_parser("list-types", help="list link types")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "show-type": _show_type,
        "list-types": _list_types
    }

    cmds[arguments.link_cmd](arguments)
