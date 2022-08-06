# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


import argparse
import sys

from torque import workspace


def _create(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    ws.create_deployment(arguments.name,
                         arguments.profile,
                         arguments.labels,
                         arguments.components)
    ws.store()


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    ws.remove_deployment(arguments.name)
    ws.store()


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if arguments.name not in ws.deployments:
        raise RuntimeError(f"{arguments.name}: deployment not found")

    print(f"{ws.deployments[arguments.name]}", file=sys.stdout)


def _list(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    for deployment in ws.deployments.values():
        print(f"{deployment}", file=sys.stdout)


def _build(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    deployment = ws.load_deployment(arguments.name)
    deployment.build(arguments.workers)


def _apply(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    deployment = ws.load_deployment(arguments.name)
    deployment.apply(arguments.workers, arguments.dry_run)


def _delete(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    deployment = ws.load_deployment(arguments.name)
    deployment.delete(arguments.dry_run)


def _dot(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    deployment = ws.load_deployment(arguments.name)
    print(deployment.dot(), file=sys.stdout)


def _command(arguments: argparse.Namespace, argv: [str]):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    deployment = ws.load_deployment(arguments.name)
    deployment.command(arguments.provider, arguments.dry_run, argv)


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("deployment", help="deployment management")
    subparsers = parser.add_subparsers(required=True, dest="deployment_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create deployment")
    create_parser.add_argument("--label", action="append", dest="labels", help="label")
    create_parser.add_argument("--component", action="append", dest="components", help="component")
    create_parser.add_argument("name", help="deployment name")
    create_parser.add_argument("profile", help="profile to use")

    remove_parser = subparsers.add_parser("remove", help="remove deployment")
    remove_parser.add_argument("name", help="deployment name")

    show_parser = subparsers.add_parser("show", help="show deployment")
    show_parser.add_argument("name", help="deployment name")

    subparsers.add_parser("list", help="list deployments")

    build_parser = subparsers.add_parser("build", help="build deployment")
    build_parser.add_argument("--workers",
                              type=int,
                              default=1,
                              help="number of build workers to use, default: %(default)s")
    build_parser.add_argument("name", help="deployment name")

    apply_parser = subparsers.add_parser("apply", help="apply deployment")
    apply_parser.add_argument("--workers",
                              type=int,
                              default=1,
                              help="number of build workers to use, default: %(default)s")
    apply_parser.add_argument("--dry-run",
                              action="store_true",
                              help="dry run")
    apply_parser.add_argument("name", help="deployment name")

    delete_parser = subparsers.add_parser("delete", help="delete deployment")
    delete_parser.add_argument("--dry-run",
                               action="store_true",
                               help="dry run")
    delete_parser.add_argument("name", help="deployment name")

    dot_parser = subparsers.add_parser("dot", help="generate dot file")
    dot_parser.add_argument("name", help="deployment name")

    command_parser = subparsers.add_parser("command", help="run a custom command")
    command_parser.add_argument("--dry-run",
                                action="store_true",
                                help="dry run")
    command_parser.add_argument("name", help="deployment name")
    command_parser.add_argument("provider", help="provider to use")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    """TODO"""

    if arguments.deployment_cmd == "command":
        _command(arguments, unparsed_argv)

    else:
        cmds = {
            "create": _create,
            "remove": _remove,
            "show": _show,
            "list": _list,
            "build": _build,
            "apply": _apply,
            "delete": _delete,
            "dot": _dot
        }

        cmds[arguments.deployment_cmd](arguments)
