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

    try:
        _layout.create_group(arguments.name, arguments.set_default)
        _layout.store()

    except exceptions.GroupExists as exc:
        raise RuntimeError(f"{arguments.name}: group exists") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.remove_group(arguments.name)
        _layout.store()

    except exceptions.GroupNotFound as exc:
        raise RuntimeError(f"{arguments.name}: group not found") from exc

    except exceptions.GroupNotEmpty as exc:
        raise RuntimeError(f"{arguments.name}: group not empty") from exc


def _set_default(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.set_default_group(arguments.name)
        _layout.store()

    except exceptions.GroupNotFound as exc:
        raise RuntimeError(f"{arguments.name}: group not found") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if arguments.name not in _layout.dag.groups:
        raise RuntimeError(f"{arguments.name}: group not found")

    print(f"{_layout.dag.groups[arguments.name]}")


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    _layout = layout.load(arguments.layout)

    for group in _layout.dag.groups.values():
        print(f"{group}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("group",
                                   description="group handling utilities",
                                   help="group management")

    subparsers = parser.add_subparsers(required=True, dest="group_cmd", metavar="command")

    create_parser = subparsers.add_parser("create",
                                          description="create group",
                                          help="create group")

    create_parser.add_argument("--set-default", action="store_true", help="set default")
    create_parser.add_argument("name", help="group name")

    remove_parser = subparsers.add_parser("remove",
                                          description="remove group",
                                          help="remove group")

    remove_parser.add_argument("name", help="group name")

    set_default_parser = subparsers.add_parser("set-default",
                                               description="set default group",
                                               help="set default group")

    set_default_parser.add_argument("name", help="group name")

    show_parser = subparsers.add_parser("show",
                                        description="show group",
                                        help="show group")

    show_parser.add_argument("name", help="group name")

    subparsers.add_parser("list", description="list groups", help="list groups")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "set-default": _set_default,
        "show": _show,
        "list": _list
    }

    cmds[arguments.group_cmd](arguments)
