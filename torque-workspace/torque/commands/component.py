# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import workspace


def _create(arguments: argparse.Namespace):
    """TODO"""

    params = workspace.process_parameters(arguments.params_file, arguments.params)
    ws = workspace.load(arguments.workspace)

    component = ws.create_component(arguments.name, arguments.type, params, arguments.no_suffix)
    ws.store()

    print(component.name)


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    ws.remove_component(arguments.name)
    ws.store()


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)
    component = ws.get_component(arguments.name)

    print(component)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)

    for component in ws.dag.components.values():
        print(component)


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    component_type = ws.repo.component(arguments.name)
    print(f"{arguments.name}: {component_type}")


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)
    component_types = ws.repo.components()

    for component in component_types:
        print(f"{component}: {component_types[component]}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("component", help="component management")
    subparsers = parser.add_subparsers(required=True, dest="component_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create component")
    create_parser.add_argument("--params-file", help="component parameters file")
    create_parser.add_argument("--param", "-p",
                               action="append",
                               metavar="NAME=VALUE",
                               dest="params",
                               help="component parameter")
    create_parser.add_argument("--no-suffix",
                               action="store_true",
                               help="don't append unique suffix to the name")
    create_parser.add_argument("name", help="component name")
    create_parser.add_argument("type", help="component type")

    remove_parser = subparsers.add_parser("remove", help="remove component")
    remove_parser.add_argument("name", help="component name")

    show_parser = subparsers.add_parser("show", help="show component")
    show_parser.add_argument("name", help="component name")

    subparsers.add_parser("list", help="list components")

    show_type_parser = subparsers.add_parser("show-type", help="show component type")
    show_type_parser.add_argument("name", help="component type name")

    subparsers.add_parser("list-types", help="list component types")


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

    cmds[arguments.component_cmd](arguments)
