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
        params = arguments.params.split(",")
        params = [i.split("=") for i in params]
        params = {i[0]: "".join(i[1:]) for i in params}

    else:
        params = {}

    try:
        link = _layout.dag.create_link(arguments.name,
                                       arguments.source,
                                       arguments.destination,
                                       arguments.type,
                                       params)

        _layout.dag.verify()

        _layout.dag.revision += 1
        _layout.store()

        for default in link.params.defaults:
            print(f"WARNING: {default}: default parameter used")

        for unused in link.params.unused:
            print(f"WARNING: {unused}: unused parameter")

    except exceptions.LinkExists as exc:
        raise RuntimeError(f"{arguments.name}: link exists") from exc

    except exceptions.ComponentNotFound as exc:
        raise RuntimeError(f"{exc}: component not found") from exc

    except exceptions.LinkTypeNotFound as exc:
        raise RuntimeError(f"{arguments.type}: link type not found") from exc

    except exceptions.ComponentsAlreadyConnected as exc:
        raise RuntimeError(f"{arguments.name}: components already connected") from exc

    except exceptions.CycleDetected as exc:
        raise RuntimeError(f"{arguments.name}: cycle detected") from exc

    except exceptions.OptionRequired as exc:
        raise RuntimeError(f"{exc}: parameter required") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.dag.remove_link(arguments.name)

        _layout.dag.revision += 1
        _layout.store()

    except exceptions.LinkNotFound as exc:
        raise RuntimeError(f"{arguments.name}: link not found") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if arguments.name not in _layout.dag.links:
        raise RuntimeError(f"{arguments.name}: link not found")

    print(f"{_layout.dag.links[arguments.name]}")


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    _layout = layout.load(arguments.layout)

    for link in _layout.dag.links.values():
        print(f"{link}")


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)
    link_types = _layout.dag.types["links.v1"]

    if arguments.name not in link_types:
        raise RuntimeError(f"{arguments.name}: link type not found")

    print(f"{arguments.name}: {link_types[arguments.name]}")


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    _layout = layout.load(arguments.layout)
    link_types = _layout.dag.types["links.v1"]

    for link in link_types:
        print(f"{link}: {link_types[link]}")


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

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "show_type": _show_type,
        "list_types": _list_types
    }

    cmds[arguments.link_cmd](arguments)
