# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from argparse import Namespace


def add_arguments(subparsers):
    """TODO"""

    subparsers.add_parser("init", help="initialize workspace")


# pylint: disable=W0613
def run(arguments: Namespace, unparsed_argv: [str]):
    """TODO"""
