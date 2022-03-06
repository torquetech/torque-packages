# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import configuration

from torque.exceptions import TorqueException
from torque.exceptions import ComponentNotFound
from torque.exceptions import ClusterNotFound


def _create(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    component_types = config["component_types"]
    components = config["components"]

    if arguments.name in components:
        raise RuntimeError(f"{arguments.name}: component exists")

    if arguments.type not in component_types:
        raise RuntimeError(f"{arguments.type}: component type not found")

    params = arguments.params.split(",")
    params = [i.split("=") for i in params]

    # component_type = component_types[arguments.type].load()
    component = configuration.Component(arguments.name,
                                        arguments.cluster,
                                        arguments.type,
                                        {i[0]: configuration.Param(i[0], "".join(i[1:])) for i in params})

    components[arguments.name] = component

    try:
        configuration.generate_dag(config)
        configuration.store(arguments.config, config)

    except ClusterNotFound as exc:
        raise RuntimeError(f"{arguments.cluster}: cluster not found") from exc

    except TorqueException as exc:
        raise RuntimeError("DAG is broken") from exc


def _remove(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    components = config["components"]

    if arguments.name not in components:
        raise RuntimeError(f"{arguments.name}: component not found")

    components.pop(arguments.name)

    try:
        configuration.generate_dag(config)
        configuration.store(arguments.config, config)

    except ComponentNotFound as exc:
        raise RuntimeError(f"{arguments.name}: component connected") from exc

    except TorqueException as exc:
        raise RuntimeError("DAG is broken") from exc


def _show(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    components = config["components"]

    if arguments.name not in components:
        raise RuntimeError(f"{arguments.name}: component not found")

    component = components[arguments.name]

    print(f"name: {component.name}")
    print(f"cluster: {component.cluster}")
    print(f"type: {component.type}")

    if len(component.params) == 0:
        return

    print("params:")
    for param in component.params.values():
        print(f"  name: {param.name}, value: {param.value}")


def _list(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    components = config["components"]

    for component in components.values():
        print(f"{component.name}")


def _show_type(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    component_types = config["component_types"]

    if arguments.name not in component_types:
        raise RuntimeError(f"{arguments.name}: component type not found")

    component = component_types[arguments.name]
    component = component.load()

    print(f"{arguments.name}:")

    print("  parameters:")
    for param in component.parameters:
        print(f"    {param.name}: {param.description}, default: {param.default_value}")

    print("  options:")
    for option in component.options:
        print(f"    {option.name}: {option.description}, default: {option.default_value}")


def _list_types(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    component_types = config["component_types"]

    for component in component_types.values():
        print(component.name)


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

    config = configuration.load(arguments.config)

    cmd = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "show_type": _show_type,
        "list_types": _list_types
    }

    cmd[arguments.component_cmd](arguments, config)
