# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import sys

import yaml

from torque import repository
from torque import v1
from torque import workspace


def _create(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)

    if arguments.no_suffix and not arguments.name:
        raise v1.exceptions.RuntimeError("if --no-suffix is specified, name must be supplied")

    link = ws.create_link(arguments.name,
                          arguments.type,
                          arguments.params,
                          arguments.labels,
                          arguments.source,
                          arguments.destination,
                          arguments.no_suffix)
    ws.store()

    print(link.name)


def _remove(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)

    ws.remove_link(arguments.name)
    ws.store()


def _describe(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)
    link = ws.get_link(arguments.name)

    yaml.safe_dump(link.describe(),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)

    yaml.safe_dump(sorted(list(ws.dag.links)),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _describe_type(arguments: argparse.Namespace):
    """DOCSTRING"""

    repo = repository.load()
    link_type = repo.link(arguments.name)

    yaml.safe_dump(link_type.describe(),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    repo = repository.load()

    yaml.safe_dump(sorted(list(repo.links())),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def add_arguments(subparsers):
    """DOCSTRING"""

    parser = subparsers.add_parser("link", help="link management")
    subparsers = parser.add_subparsers(required=True, dest="link_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create link")
    create_parser.add_argument("--param", "-p",
                               action="append",
                               metavar="NAME=VALUE",
                               dest="params",
                               help="link parameter")
    create_parser.add_argument("--label", "-l",
                               action="append",
                               metavar="NAME=VALUE",
                               dest="labels",
                               help="link label")
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

    describe_parser = subparsers.add_parser("describe", help="describe link")
    describe_parser.add_argument("name", help="link name")

    subparsers.add_parser("list", help="list links")

    describe_type_parser = subparsers.add_parser("describe-type",
                                                 help="describe link type")
    describe_type_parser.add_argument("name", help="link type name")

    subparsers.add_parser("list-types", help="list link types")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """DOCSTRING"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "describe": _describe,
        "list": _list,
        "describe-type": _describe_type,
        "list-types": _list_types
    }

    cmds[arguments.link_cmd](arguments)
