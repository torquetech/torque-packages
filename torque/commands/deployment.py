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

    if arguments.groups:
        groups = arguments.groups.split(",")

    else:
        groups = []

    if arguments.components:
        components = arguments.components.split(",")

    else:
        components = []

    try:
        ws.create_deployment(arguments.name,
                             arguments.profile,
                             groups,
                             components)
        ws.store()

    except exceptions.DeploymentExists as exc:
        raise RuntimeError(f"{arguments.name}: deployment exists") from exc

    except exceptions.ProviderNotFound as exc:
        raise RuntimeError(f"{arguments.profile}: profile not found") from exc

    except exceptions.GroupNotFound as exc:
        raise RuntimeError(f"{exc}: group not found") from exc

    except exceptions.ComponentNotFound as exc:
        raise RuntimeError(f"{exc}: component not found") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        ws.remove_deployment(arguments.name)
        ws.store()

    except exceptions.DeploymentNotFound as exc:
        raise RuntimeError(f"{arguments.name}: deployment not found") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if arguments.name not in ws.deployments:
        raise RuntimeError(f"{arguments.name}: deployment not found")

    print(f"{ws.deployments[arguments.name]}")


def _list(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    for deployment in ws.deployments.values():
        print(f"{deployment}")


def _build(arguments: argparse.Namespace):
    """TODO"""


def _apply(arguments: argparse.Namespace):
    """TODO"""


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("deployment", help="deployment management")
    subparsers = parser.add_subparsers(required=True, dest="deployment_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create deployment")
    create_parser.add_argument("--groups", help="groups to use")
    create_parser.add_argument("--components", help="components to use")
    create_parser.add_argument("name", help="deployment name")
    create_parser.add_argument("profile", help="profile to use")

    remove_parser = subparsers.add_parser("remove", help="remove deployment")
    remove_parser.add_argument("name", help="deployment name")

    show_parser = subparsers.add_parser("show", help="show deployment")
    show_parser.add_argument("name", help="deployment name")

    subparsers.add_parser("list", help="list deployments")

    build_parser = subparsers.add_parser("build", help="build deployment")
    build_parser.add_argument("name", help="deployment name")

    apply_parser = subparsers.add_parser("apply", help="apply deployment")
    apply_parser.add_argument("name", help="deployment name")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "build": _build,
        "apply": _apply
    }

    cmds[arguments.deployment_cmd](arguments)
