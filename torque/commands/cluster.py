# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse

from torque import configuration

from torque.exceptions import DuplicateCluster
from torque.exceptions import ClusterNotFound


def _create(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    clusters = config["clusters"]

    if arguments.name in clusters:
        raise RuntimeError(f"{arguments.name}: cluster exists")

    clusters[arguments.name] = configuration.Cluster(arguments.name)

    try:
        configuration.generate_dag(config)
        configuration.store(arguments.config, config)

    except DuplicateCluster as exc:
        raise RuntimeError(f"{arguments.name}: cluster exists") from exc


def _remove(arguments: argparse.Namespace, config: configuration.Config):
    """TODO"""

    clusters = config["clusters"]

    if arguments.name not in clusters:
        raise RuntimeError(f"{arguments.name}: cluster not found")

    clusters.pop(arguments.name)

    try:
        configuration.generate_dag(config)
        configuration.store(arguments.config, config)

    except ClusterNotFound as exc:
        raise RuntimeError(f"{arguments.name}: cluster not empty") from exc


def _list(arguments: argparse.Namespace, config: configuration.Config):
    # pylint: disable=W0613

    """TODO"""

    clusters = config["clusters"]

    for cluster in clusters.values():
        print(f"{cluster.name}")


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

    config = configuration.load(arguments.config)

    cmd = {
        "create": _create,
        "remove": _remove,
        "list": _list
    }

    cmd[arguments.cluster_cmd](arguments, config)
