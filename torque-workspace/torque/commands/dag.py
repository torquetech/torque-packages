# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""


import argparse

from torque import workspace


def _dot(arguments: argparse.Namespace):
    """DOCSTRING"""

    ws = workspace.load(arguments.workspace)
    dag = ws.dag.filter(arguments.filters,
                        arguments.components)

    print(dag.dot("workspace"))


def add_arguments(subparsers):
    """DOCSTRING"""

    parser = subparsers.add_parser("dag", help="DAG utilities")
    subparsers = parser.add_subparsers(required=True,
                                       dest="dag_cmd",
                                       metavar="command")

    dot_parser = subparsers.add_parser("dot", help="generate dot file")
    dot_parser.add_argument("--filter",
                            action="append",
                            metavar="FILTER",
                            dest="filters",
                            help="filter expression")
    dot_parser.add_argument("--component",
                            action="append",
                            metavar="COMPONENT",
                            dest="components",
                            help="component name")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """DOCSTRING"""

    cmds = {
        "dot": _dot
    }

    cmds[arguments.dag_cmd](arguments)
