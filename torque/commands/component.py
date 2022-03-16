# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import exceptions
from torque import layout


def _create(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if arguments.params:
        raw_params = arguments.params.split(",")
        raw_params = [i.split("=") for i in raw_params]
        raw_params = {i[0]: "".join(i[1:]) for i in raw_params}

    else:
        raw_params = {}

    if arguments.group:
        group = arguments.group

    else:
        group = _layout.config.default_group

    if not group:
        raise RuntimeError("group not specified")

    try:
        component = _layout.create_component(arguments.name, group, arguments.type, raw_params)

        for default in component.params.defaults:
            print(f"WARNING: {default}: default parameter used")

        for unused in component.params.unused:
            print(f"WARNING: {unused}: unused parameter")

        _layout.store()

    except exceptions.ComponentExists as exc:
        raise RuntimeError(f"{arguments.name}: component exists") from exc

    except exceptions.GroupNotFound as exc:
        raise RuntimeError(f"{arguments.group}: group not found") from exc

    except exceptions.ComponentTypeNotFound as exc:
        raise RuntimeError(f"{arguments.type}: component type not found") from exc

    except exceptions.OptionRequired as exc:
        raise RuntimeError(f"{exc}: parameter required") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.remove_component(arguments.name)

        _layout.store()

    except exceptions.ComponentNotFound as exc:
        raise RuntimeError(f"{arguments.name}: component not found") from exc

    except exceptions.ComponentStillConnected as exc:
        raise RuntimeError(f"{arguments.name}: component still connected") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if arguments.name not in _layout.dag.components:
        raise RuntimeError(f"{arguments.name}: component not found")

    print(f"{_layout.dag.components[arguments.name]}")


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    _layout = layout.load(arguments.layout)

    for component in _layout.dag.components.values():
        print(f"{component}")


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        component_type = _layout.types.component(arguments.name)
        print(f"{arguments.name}: {component_type}")

    except exceptions.ComponentTypeNotFound as exc:
        raise RuntimeError(f"{arguments.name}: component type not found") from exc


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    _layout = layout.load(arguments.layout)
    component_types = _layout.types.components()

    for component in component_types:
        print(f"{component}: {component_types[component]}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("component",
                                   description="component handling utilities",
                                   help="component management")

    subparsers = parser.add_subparsers(required=True,
                                       dest="component_cmd",
                                       metavar="command")

    create_parser = subparsers.add_parser("create",
                                          description="create component",
                                          help="create component")

    create_parser.add_argument("--params", "-p", help="component params")
    create_parser.add_argument("--group", help="component group membership")
    create_parser.add_argument("name", help="component name")
    create_parser.add_argument("type", help="component type")

    remove_parser = subparsers.add_parser("remove",
                                          description="remove component",
                                          help="remove component")

    remove_parser.add_argument("name", help="component name")

    show_parser = subparsers.add_parser("show",
                                        description="show component",
                                        help="show component")

    show_parser.add_argument("name", help="component name")

    subparsers.add_parser("list",
                          description="list components",
                          help="list components")

    show_type_parser = subparsers.add_parser("show-type",
                                             description="show component type",
                                             help="show component type")

    show_type_parser.add_argument("name", help="component type name")

    subparsers.add_parser("list-types",
                          description="list component types",
                          help="list component types")


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
