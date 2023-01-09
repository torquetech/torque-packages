# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import sys

import yaml

from torque import repository
from torque import v1


def _describe_type(arguments: argparse.Namespace):
    """DOCSTRING"""

    repo = repository.load()
    bond_type = repo.bond(arguments.name)

    yaml.safe_dump(bond_type.describe(),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """DOCSTRING"""

    repo = repository.load()
    bonds = {} | repo.bonds()

    for name in list(bonds.keys()):
        bond = bonds[name]

        if arguments.interface:
            if v1.utils.fqcn(bond.IMPLEMENTS) != arguments.interface:
                bonds.pop(name, None)

        if arguments.provider:
            if v1.utils.fqcn(bond.PROVIDER) != arguments.provider:
                bonds.pop(name, None)

    yaml.safe_dump(sorted(list(bonds)),
                   stream=sys.stdout,
                   default_flow_style=False,
                   sort_keys=False)


def add_arguments(subparsers):
    """DOCSTRING"""

    parser = subparsers.add_parser("bond", help="bond information")
    subparsers = parser.add_subparsers(required=True, dest="bond_cmd", metavar="command")

    describe_parser = subparsers.add_parser("describe-type", help="describe bond")
    describe_parser.add_argument("name", help="bond name")

    list_parser = subparsers.add_parser("list-types", help="list bonds")
    list_parser.add_argument("--interface", help="interface filter")
    list_parser.add_argument("--provider", help="provider filter")


def run(arguments: argparse.Namespace, unparsed_argv: [str]):
    # pylint: disable=W0613

    """DOCSTRING"""

    cmds = {
        "describe-type": _describe_type,
        "list-types": _list_types
    }

    cmds[arguments.bond_cmd](arguments)
