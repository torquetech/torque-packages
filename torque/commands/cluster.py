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
        _layout.dag.create_cluster(arguments.name)

        if arguments.set_default:
            _layout.config.default_cluster = arguments.name

        _layout.dag.revision += 1
        _layout.store()

    except exceptions.ClusterExists as exc:
        raise RuntimeError(f"{arguments.name}: cluster exists") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    try:
        _layout.dag.remove_cluster(arguments.name)

        _layout.dag.revision += 1
        _layout.store()

    except exceptions.ClusterNotFound as exc:
        raise RuntimeError(f"{arguments.name}: cluster not found") from exc

    except exceptions.ClusterNotEmpty as exc:
        raise RuntimeError(f"{arguments.name}: cluster not empty") from exc


def _set_default(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if not _layout.dag.has_cluster(arguments.name):
        raise RuntimeError(f"{arguments.name}: cluster not found")

    _layout.config.default_cluster = arguments.name

    _layout.store()


def _show(arguments: argparse.Namespace):
    """TODO"""

    _layout = layout.load(arguments.layout)

    if arguments.name not in _layout.dag.clusters:
        raise RuntimeError(f"{arguments.name}: cluster not found")

    print(f"{_layout.dag.clusters[arguments.name]}")


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    _layout = layout.load(arguments.layout)

    for cluster in _layout.dag.clusters.values():
        print(f"{cluster}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("cluster",
                                   description="cluster handling utilities",
                                   help="cluster management")

    subparsers = parser.add_subparsers(required=True, dest="cluster_cmd", metavar="command")

    create_parser = subparsers.add_parser("create",
                                          description="create cluster",
                                          help="create cluster")

    create_parser.add_argument("--set-default", action="store_true", help="set default")
    create_parser.add_argument("name", help="cluster name")

    remove_parser = subparsers.add_parser("remove",
                                          description="remove cluster",
                                          help="remove cluster")

    remove_parser.add_argument("name", help="cluster name")

    set_default_parser = subparsers.add_parser("set-default",
                                               description="set default cluster",
                                               help="set default cluster")

    set_default_parser.add_argument("name", help="cluster name")

    show_parser = subparsers.add_parser("show",
                                        description="show cluster",
                                        help="show cluster")

    show_parser.add_argument("name", help="cluster name")

    subparsers.add_parser("list", description="list clusters", help="list clusters")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "set-default": _set_default,
        "show": _show,
        "list": _list
    }

    cmds[arguments.cluster_cmd](arguments)
