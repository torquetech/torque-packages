# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import os
import sys
import traceback

from torque.package import install_deps

# pylint: disable=C0413
if os.path.isfile(".torque/cache/install_deps"):
    install_deps(True, True)


from torque.commands import init
from torque.commands import package
from torque.commands import cluster
from torque.commands import component
from torque.commands import link
from torque.commands import build
from torque.commands import push
from torque.commands import generate
from torque.commands import install
from torque.commands import uninstall


def main() -> int:
    """TODO"""

    verbose = os.getenv("VERBOSE") is not None

    # pylint: disable=W0703
    try:
        parser = argparse.ArgumentParser(prog="torque", description="torque command line interface.")
        subparsers = parser.add_subparsers(required=True, dest="main_cmd", metavar="command")

        parser.add_argument("--config",
                            default=".torque/config.yaml",
                            metavar="PATH",
                            help="configuration file to use")

        commands = {
            "init": init,
            "package": package,
            "cluster": cluster,
            "component": component,
            "link": link,
            "build": build,
            "push": push,
            "generate": generate,
            "install": install,
            "uninstall": uninstall
        }

        for cmd in commands.values():
            cmd.add_arguments(subparsers)

        args = parser.parse_args()

        commands[args.main_cmd].run(args)

        return 0

    except Exception as exc:
        if verbose:
            traceback.print_exc()

        else:
            print(exc)

    return 1


if __name__ == "__main__":
    sys.exit(main())
