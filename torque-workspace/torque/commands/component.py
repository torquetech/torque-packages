# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import sys

import yaml

from torque import repository
from torque import workspace


def _create(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)

    component = ws.create_component(arguments.name,
                                    arguments.type,
                                    arguments.params,
                                    arguments.labels,
                                    arguments.no_suffix)
    ws.store()

    print(component.name)


def _remove(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)

    ws.remove_component(arguments.name)
    ws.store()


def _describe(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)
    component = ws.get_component(arguments.name)

    yaml.safe_dump(component.describe(),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)

    yaml.safe_dump(sorted(list(ws.dag.components)),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _describe_type(arguments: argparse.Namespace):
    """DOCSTRING"""

    repo = repository.load()
    component_type = repo.component(arguments.name)

    yaml.safe_dump(component_type.describe(),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    repo = repository.load()

    yaml.safe_dump(sorted(list(repo.components())),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def add_arguments(subparsers):
    """DOCSTRING"""

    parser = subparsers.add_parser("component", help="component management")
    subparsers = parser.add_subparsers(required=True, dest="component_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create component")
    create_parser.add_argument("--param", "-p",
                               action="append",
                               metavar="NAME=VALUE",
                               dest="params",
                               help="component parameter")
    create_parser.add_argument("--label", "-l",
                               action="append",
                               metavar="NAME=VALUE",
                               dest="labels",
                               help="component label")
    create_parser.add_argument("--no-suffix",
                               action="store_true",
                               help="don't append unique suffix to the name")
    create_parser.add_argument("name", help="component name")
    create_parser.add_argument("type", help="component type")

    remove_parser = subparsers.add_parser("remove", help="remove component")
    remove_parser.add_argument("name", help="component name")

    describe_parser = subparsers.add_parser("describe", help="describe component")
    describe_parser.add_argument("name", help="component name")

    subparsers.add_parser("list", help="list components")

    describe_type_parser = subparsers.add_parser("describe-type",
                                                 help="describe component type")
    describe_type_parser.add_argument("name", help="component type name")

    subparsers.add_parser("list-types", help="list component types")


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

    cmds[arguments.component_cmd](arguments)
