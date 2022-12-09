# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


import argparse
import sys

import yaml

from torque import v1
from torque import workspace


def _create(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)

    d = ws.create_deployment(arguments.name,
                             arguments.context,
                             arguments.provider,
                             arguments.extra_configs,
                             arguments.components,
                             arguments.strict,
                             arguments.no_suffix)
    deployment = ws.load_deployment(d.name, False)

    deployment.update()
    deployment.store()

    ws.store()

    print(d.name)


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)

    ws.remove_deployment(arguments.name)
    ws.store()


def _update(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)
    deployment = ws.load_deployment(arguments.name, False, False)

    deployment.update()
    deployment.store()


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)
    deployment = ws.load_deployment(arguments.name, False)

    print(deployment)


def _list(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)

    for deployment in ws.deployments.values():
        print(deployment)


def _build(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)
    deployment = ws.load_deployment(arguments.name)

    try:
        deployment.build(arguments.workers)

    finally:
        deployment.store()


def _apply(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)
    deployment = ws.load_deployment(arguments.name)

    try:
        deployment.apply(arguments.workers)

    finally:
        deployment.store()


def _delete(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)
    deployment = ws.load_deployment(arguments.name)

    try:
        deployment.delete()

    finally:
        deployment.store()


def _get(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)

    deployment = ws.load_deployment(arguments.name)
    data = deployment.load_object(arguments.object)

    yaml.safe_dump(data,
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _set(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)

    deployment = ws.load_deployment(arguments.name)
    data = yaml.safe_load(sys.stdin)

    deployment.store_object(arguments.object, data)


def _dot(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace, arguments.deployments)

    deployment = ws.load_deployment(arguments.name)
    print(deployment.dot())


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("deployment", help="deployment management")
    parser.add_argument("--deployments",
                        default=f"{v1.utils.torque_root()}/.torque/deployments.yaml",
                        metavar="PATH",
                        help="deployments path, default: %(default)s")

    subparsers = parser.add_subparsers(required=True,
                                       dest="deployment_cmd",
                                       metavar="command")

    create_parser = subparsers.add_parser("create", help="create deployment")
    create_parser.add_argument("--strict",
                               action="store_true",
                               help="create strict deployment")
    create_parser.add_argument("--context",
                               default="torque.defaults.V1LocalContext",
                               help="deployment context, default: %(default)s")
    create_parser.add_argument("--extra-config",
                               action="append",
                               metavar="CONFIG",
                               dest="extra_configs",
                               help="extra deployment configuration")
    create_parser.add_argument("--component",
                               action="append",
                               metavar="COMPONENT",
                               dest="components",
                               help="component")
    create_parser.add_argument("--no-suffix",
                               action="store_true",
                               help="don't append unique suffix to the name")
    create_parser.add_argument("name", help="deployment name")
    create_parser.add_argument("provider", nargs="+", help="provider name")

    remove_parser = subparsers.add_parser("remove", help="remove deployment")
    remove_parser.add_argument("name", help="deployment name")

    update_parser = subparsers.add_parser("update", help="update deployment")
    update_parser.add_argument("name", help="deployment name")

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
    apply_parser.add_argument("name", help="deployment name")

    delete_parser = subparsers.add_parser("delete", help="delete deployment")
    delete_parser.add_argument("name", help="deployment name")

    get_parser = subparsers.add_parser("get", help="get context object")
    get_parser.add_argument("name", help="deployment name")
    get_parser.add_argument("object", help="object name")

    set_parser = subparsers.add_parser("set", help="set context object")
    set_parser.add_argument("name", help="deployment name")
    set_parser.add_argument("object", help="object name")

    dot_parser = subparsers.add_parser("dot", help="generate dot file")
    dot_parser.add_argument("name", help="deployment name")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "update": _update,
        "show": _show,
        "list": _list,
        "build": _build,
        "apply": _apply,
        "delete": _delete,
        "get": _get,
        "set": _set,
        "dot": _dot
    }

    cmds[arguments.deployment_cmd](arguments)
