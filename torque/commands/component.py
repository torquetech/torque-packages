# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import exceptions
from torque import workspace


def _create(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if arguments.params:
        raw_params = arguments.params.split(",")
        raw_params = [i.split("=") for i in raw_params]
        raw_params = {i[0]: "".join(i[1:]) for i in raw_params}

    else:
        raw_params = {}

    if arguments.group:
        group = arguments.group

    else:
        group = ws.config.default_group

    if not group:
        raise RuntimeError("group not specified")

    try:
        component = ws.create_component(arguments.name, group, arguments.type, raw_params)

        for default in component.params.defaults:
            print(f"WARNING: {default}: default parameter used")

        for unused in component.params.unused:
            print(f"WARNING: {unused}: unused parameter")

        ws.store()

    except exceptions.ComponentExists as exc:
        raise RuntimeError(f"{arguments.name}: component exists") from exc

    except exceptions.GroupNotFound as exc:
        raise RuntimeError(f"{arguments.group}: group not found") from exc

    except exceptions.ComponentTypeNotFound as exc:
        raise RuntimeError(f"{arguments.type}: component type not found") from exc

    except exceptions.OptionRequired as exc:
        raise RuntimeError(f"{exc}: parameter required") from exc

    except exceptions.InvalidName as exc:
        raise RuntimeError(f"{arguments.name}: invalid name") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        ws.remove_component(arguments.name)

        ws.store()

    except exceptions.ComponentNotFound as exc:
        raise RuntimeError(f"{arguments.name}: component not found") from exc

    except exceptions.ComponentStillConnected as exc:
        raise RuntimeError(f"{arguments.name}: component still connected") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if arguments.name not in ws.dag.components:
        raise RuntimeError(f"{arguments.name}: component not found")

    print(f"{ws.dag.components[arguments.name]}")


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)

    for component in ws.dag.components.values():
        print(f"{component}")


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        component_type = ws.exts.component(arguments.name)
        print(f"{arguments.name}: {component_type}")

    except exceptions.ComponentTypeNotFound as exc:
        raise RuntimeError(f"{arguments.name}: component type not found") from exc


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)
    component_types = ws.exts.components()

    for component in component_types:
        print(f"{component}: {component_types[component]}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("component", help="component management")
    subparsers = parser.add_subparsers(required=True, dest="component_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create component")
    create_parser.add_argument("--params", "-p", help="component params")
    create_parser.add_argument("--group", help="component group membership")
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


def run(arguments: argparse.Namespace):
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
