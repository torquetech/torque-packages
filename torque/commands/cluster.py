# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import configuration
from torque import exceptions


def _create(arguments: argparse.Namespace):
    """TODO"""

    dag, profiles = configuration.load(arguments.config)

    try:
        dag.create_cluster(arguments.name)

    except exceptions.ClusterExists as exc:
        raise RuntimeError(f"{arguments.name}: cluster exists") from exc

    configuration.store(arguments.config, dag, profiles)


def _remove(arguments: argparse.Namespace):
    """TODO"""

    dag, profiles = configuration.load(arguments.config)

    try:
        dag.remove_cluster(arguments.name)

    except exceptions.ClusterNotFound as exc:
        raise RuntimeError(f"{arguments.name}: cluster not found") from exc

    except exceptions.ClusterNotEmpty as exc:
        raise RuntimeError(f"{arguments.name}: cluster not empty") from exc

    configuration.store(arguments.config, dag, profiles)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    dag, _ = configuration.load(arguments.config)

    for cluster in dag.clusters.values():
        print(f"{cluster}")


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("cluster",
                                   description="cluster handling utilities",
                                   help="cluster management")

    subparsers = parser.add_subparsers(required=True, dest="cluster_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", description="create cluster", help="create cluster")
    create_parser.add_argument("name", help="cluster name")

    remove_parser = subparsers.add_parser("remove", description="remove cluster", help="remove cluster")
    remove_parser.add_argument("name", help="cluster name")

    subparsers.add_parser("list", description="list clusters", help="list clusters")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmd = {
        "create": _create,
        "remove": _remove,
        "list": _list
    }

    cmd[arguments.cluster_cmd](arguments)
