# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from argparse import Namespace


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("install", description="install targets", help="install targets")


def run(arguments: Namespace):
    """TODO"""

    print(arguments)
