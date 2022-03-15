# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import sys
import schema

from torque import exceptions
from torque import layout


def _create(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.create_profile(arguments.name, arguments.uri, arguments.secret)
        _layout.store()

    except exceptions.ProfileExists as exc:
        raise RuntimeError(f"{arguments.name}: profile exists") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.remove_profile(arguments.name)
        _layout.store()

    except exceptions.ProfileNotFound as exc:
        raise RuntimeError(f"{arguments.name}: profile not found") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if arguments.name not in _layout.profiles:
        raise RuntimeError(f"{arguments.name}: profile not found")

    print(f"{_layout.profiles[arguments.name]}")


def _export(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        config = _layout.load_profile(arguments.name)
        config.dump(sys.stdout)

    except exceptions.ProfileNotFound as exc:
        raise RuntimeError(f"{arguments.name}: profile not found") from exc

    except schema.SchemaError as exc:
        raise RuntimeError(f"{arguments.name}: invalid configuration") from exc


def _list(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    for profile in _layout.profiles.values():
        print(f"{profile}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("profile",
                                   description="profile handling utilities",
                                   help="profile management")

    subparsers = parser.add_subparsers(required=True,
                                       dest="profile_cmd",
                                       metavar="command")

    create_parser = subparsers.add_parser("create",
                                          description="create profile",
                                          help="create profile")

    create_parser.add_argument("--secret", help="configuration uri secret")
    create_parser.add_argument("name", help="profile name")
    create_parser.add_argument("uri", help="configuration uri")

    remove_parser = subparsers.add_parser("remove",
                                          description="remove profile",
                                          help="remove profile")

    remove_parser.add_argument("name", help="profile name")

    show_parser = subparsers.add_parser("show",
                                        description="show profile",
                                        help="show profile")

    show_parser.add_argument("name", help="profile name")

    export_parser = subparsers.add_parser("export",
                                          description="export profile",
                                          help="export profile")

    export_parser.add_argument("name", help="profile name")

    subparsers.add_parser("list",
                          description="list profiles",
                          help="list profiles")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "export": _export,
        "list": _list
    }

    cmds[arguments.profile_cmd](arguments)
