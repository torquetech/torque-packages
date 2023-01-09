# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import sys

import yaml

from torque import repository


def _describe_type(arguments: argparse.Namespace):
    """DOCSTRING"""

    repo = repository.load()
    context_type = repo.context(arguments.name)

    yaml.safe_dump(context_type.describe(),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    repo = repository.load()

    yaml.safe_dump(sorted(list(repo.contexts())),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def add_arguments(subparsers):
    """DOCSTRING"""

    parser = subparsers.add_parser("context", help="context information")
    subparsers = parser.add_subparsers(required=True, dest="context_cmd", metavar="command")

    describe_parser = subparsers.add_parser("describe-type", help="describe context")
    describe_parser.add_argument("name", help="context name")

    subparsers.add_parser("list-types", help="list contexts")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """DOCSTRING"""

    cmds = {
        "describe-type": _describe_type,
        "list-types": _list_types
    }

    cmds[arguments.context_cmd](arguments)
