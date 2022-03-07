# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import exceptions
from torque import layout


def _create(arguments: argparse.Namespace):
    """TODO"""

    dag, profiles = layout.load(arguments.layout)

    if arguments.params:
        params = arguments.params.split(",")
        params = [i.split("=") for i in params]

    else:
        params = {}

    try:
        dag.create_component(arguments.name,
                             arguments.cluster,
                             arguments.type,
                             {i[0]: "".join(i[1:]) for i in params})

    except exceptions.ComponentExists as exc:
        raise RuntimeError(f"{arguments.name}: component exists") from exc

    except exceptions.ClusterNotFound as exc:
        raise RuntimeError(f"{arguments.cluster}: cluster not found") from exc

    except exceptions.ComponentTypeNotFound as exc:
        raise RuntimeError(f"{arguments.type}: component type not found") from exc

    layout.store(arguments.layout, dag, profiles)


def _remove(arguments: argparse.Namespace):
    """TODO"""

    dag, profiles = layout.load(arguments.layout)

    try:
        dag.remove_component(arguments.name)

    except exceptions.ComponentNotFound as exc:
        raise RuntimeError(f"{arguments.name}: component not found") from exc

    except exceptions.ComponentStillConnected as exc:
        raise RuntimeError(f"{arguments.name}: component still connected") from exc

    layout.store(arguments.layout, dag, profiles)


def _show(arguments: argparse.Namespace):
    """TODO"""

    dag, _ = layout.load(arguments.layout)

    if arguments.name not in dag.components:
        raise RuntimeError(f"{arguments.name}: component not found")

    print(f"{dag.components[arguments.name]}")


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    dag, _ = layout.load(arguments.layout)

    for component in dag.components.values():
        print(f"{component}")


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    dag, _ = layout.load(arguments.layout)
    component_types = dag.types["components.v1"]

    if arguments.name not in component_types:
        raise RuntimeError(f"{arguments.name}: component type not found")

    print(f"{arguments.name}: {component_types[arguments.name]}")


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    dag, _ = layout.load(arguments.layout)
    component_types = dag.types["components.v1"]

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
    create_parser.add_argument("name", help="component name")
    create_parser.add_argument("cluster", help="component cluster membership")
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

    show_type_parser = subparsers.add_parser("show_type",
                                             description="show component type",
                                             help="show component type")

    show_type_parser.add_argument("name", help="component type name")

    subparsers.add_parser("list_types",
                          description="list component types",
                          help="list component types")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "show_type": _show_type,
        "list_types": _list_types
    }

    cmds[arguments.component_cmd](arguments)
