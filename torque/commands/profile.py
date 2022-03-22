# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import sys
import schema

from torque import exceptions
from torque import workspace


def _create(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        ws.create_profile(arguments.name, arguments.uri, arguments.secret)
        ws.store()

    except exceptions.ProfileExists as exc:
        raise RuntimeError(f"{arguments.name}: profile exists") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        ws.remove_profile(arguments.name)
        ws.store()

    except exceptions.ProfileNotFound as exc:
        raise RuntimeError(f"{arguments.name}: profile not found") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if arguments.name not in ws.profiles:
        raise RuntimeError(f"{arguments.name}: profile not found")

    print(f"{ws.profiles[arguments.name]}")


def _export(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        config = ws.load_profile(arguments.name)
        config.dump(sys.stdout)

    except exceptions.ProfileNotFound as exc:
        raise RuntimeError(f"{arguments.name}: profile not found") from exc

    except schema.SchemaError as exc:
        raise RuntimeError(f"{arguments.name}: invalid configuration") from exc


def _list(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    for profile in ws.profiles.values():
        print(f"{profile}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("profile", help="profile management")
    subparsers = parser.add_subparsers(required=True, dest="profile_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create profile")

    create_parser.add_argument("--secret", help="configuration uri secret")
    create_parser.add_argument("name", help="profile name")
    create_parser.add_argument("uri", help="configuration uri")

    remove_parser = subparsers.add_parser("remove", help="remove profile")
    remove_parser.add_argument("name", help="profile name")

    show_parser = subparsers.add_parser("show", help="show profile")
    show_parser.add_argument("name", help="profile name")

    export_parser = subparsers.add_parser("export", help="export profile")
    export_parser.add_argument("name", help="profile name")

    subparsers.add_parser("list", help="list profiles")


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
