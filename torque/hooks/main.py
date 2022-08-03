# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import os
import sys

from torque import commands
from torque import v1


def fix_paths():
    """TODO"""

    if sys.path[0] == os.getcwd():
        sys.path = sys.path[1:]


def main() -> int:
    """TODO"""

    # For 'python -m module' python always puts in current directory
    # as the first path element and that can mess up the whole environment
    # if the current directory has a file or a directory with the same
    # name as some torque and/or system module. Fix it here util it's
    # fixed upstream.
    fix_paths()

    # pylint: disable=W0703
    try:
        parser = argparse.ArgumentParser(prog="torque", description="torque command line interface.")
        subparsers = parser.add_subparsers(required=True, dest="main_cmd", metavar="command")

        parser.add_argument("--workspace",
                            default=f"{v1.utils.torque_root()}/.torque/workspace.yaml",
                            metavar="PATH",
                            help="workspace file to use")

        cmds = {
            "init": commands.init,
            "package": commands.package,
            "profile": commands.profile,
            "component": commands.component,
            "link": commands.link,
            "deployment": commands.deployment
        }

        for cmd in cmds.values():
            cmd.add_arguments(subparsers)

        args = parser.parse_args()

        cmds[args.main_cmd].run(args)

        return 0

    except RuntimeError as exc:
        print(exc, file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
