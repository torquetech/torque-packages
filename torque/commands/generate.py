# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("generate", description="generate targets", help="generate targets")


def run(arguments: argparse.Namespace):
    """TODO"""

    print(arguments)
