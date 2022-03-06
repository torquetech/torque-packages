# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import configuration

from torque.exceptions import TorqueException
from torque.exceptions import LinkAlreadyExists


def _create(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    components = config["components"]

    link_types = config["link_types"]
    links = config["links"]

    if arguments.name in links:
        raise RuntimeError(f"{arguments.name}: link exists")

    if arguments.type not in link_types:
        raise RuntimeError(f"{arguments.type}: link type not found")

    if arguments.source not in components:
        raise RuntimeError(f"{arguments.source}: component not found")

    if arguments.destination not in components:
        raise RuntimeError(f"{arguments.destination}: component not found")

    if arguments.source == arguments.destination:
        raise RuntimeError("can't connect component to itself")

    params = arguments.params.split(",")
    params = [i.split("=") for i in params]

    # link_type = link_types[arguments.type].load()
    link = configuration.Link(arguments.name,
                              arguments.source,
                              arguments.destination,
                              arguments.type,
                              {i[0]: configuration.Param(i[0], "".join(i[1:])) for i in params})

    links[arguments.name] = link

    try:
        configuration.generate_dag(config)
        configuration.store(arguments.config, config)

    except LinkAlreadyExists as exc:
        raise RuntimeError("components already connected") from exc

    except TorqueException as exc:
        raise RuntimeError("DAG is broken") from exc


def _remove(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    links = config["links"]

    if arguments.name not in links:
        raise RuntimeError(f"{arguments.name}: link not found")

    links.pop(arguments.name)

    try:
        configuration.generate_dag(config)
        configuration.store(arguments.config, config)

    except TorqueException as exc:
        raise RuntimeError("DAG is broken") from exc


def _show(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    links = config["links"]

    if arguments.name not in links:
        raise RuntimeError(f"{arguments.name}: link not found")

    link = links[arguments.name]

    print(f"name: {link.name}")
    print(f"source: {link.source}")
    print(f"destination: {link.destination}")
    print(f"type: {link.type}")

    if len(link.params) == 0:
        return

    print("params:")
    for param in link.params.values():
        print(f"  name: {param.name}, value: {param.value}")


def _list(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    links = config["links"]

    for link in links.values():
        print(f"{link.name}")


def _show_type(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    link_types = config["link_types"]

    if arguments.name not in link_types:
        raise RuntimeError(f"{arguments.name}: link type not found")

    link = link_types[arguments.name]
    link = link.load()

    print(f"{arguments.name}:")

    print("  parameters:")
    for param in link.parameters:
        print(f"    {param.name}: {param.description}, default: {param.default_value}")

    print("  options:")
    for option in link.options:
        print(f"    {option.name}: {option.description}, default: {option.default_value}")


def _list_types(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    link_types = config["link_types"]

    for component in link_types.values():
        print(component.name)


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("link",
                                   description="link handling utilities",
                                   help="link management")

    subparsers = parser.add_subparsers(required=True,
                                       dest="link_cmd",
                                       metavar="command")

    create_parser = subparsers.add_parser("create",
                                          description="create link",
                                          help="create link")

    create_parser.add_argument("--params", "-p", help="link params")
    create_parser.add_argument("name", help="link name")
    create_parser.add_argument("source", help="source component")
    create_parser.add_argument("destination", help="destination component")
    create_parser.add_argument("type", help="link type")

    remove_parser = subparsers.add_parser("remove",
                                          description="remove link",
                                          help="remove link")

    remove_parser.add_argument("name", help="link name")

    show_parser = subparsers.add_parser("show",
                                        description="show link",
                                        help="show link")

    show_parser.add_argument("name", help="link name")

    subparsers.add_parser("list",
                          description="list links",
                          help="list links")

    show_type_parser = subparsers.add_parser("show_type",
                                             description="show link type",
                                             help="show link type")

    show_type_parser.add_argument("name", help="link type name")

    subparsers.add_parser("list_types",
                          description="list link types",
                          help="list link types")


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

    cmd[arguments.link_cmd](arguments, config)
