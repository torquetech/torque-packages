# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import os
import subprocess
import sys

from torque import init
from torque import workspace


class InvalidWorkspace(Exception):
    """TODO"""


def find_workspace_root():
    """TODO"""

    while True:
        cwd = os.getcwd()

        if os.path.isdir(".torque"):
            return True

        if cwd == "/":
            return False

        os.chdir("..")


def pass_through_command(argv, cwd: str):
    """TODO"""

    cmd = [
        ".torque/local/venv/bin/python",
        "-m", "torque"
    ]

    cmd += argv

    env = os.environ | {
        "VIRTUAL_ENV": ".torque/local/venv",
        "TORQUE_CWD": cwd
    }

    subprocess.run(cmd, env=env, check=True)


def main() -> int:
    """TODO"""

    # pylint: disable=W0703
    try:
        if len(sys.argv) > 1:
            parser = argparse.ArgumentParser(description="torque command line interface.")
            subparsers = parser.add_subparsers(required=True,
                                               dest="main_cmd",
                                               metavar="command")

            init.add_arguments(subparsers)

            if sys.argv[1] == "init":
                init.run(parser.parse_args())

                return 0

        cwd = os.getcwd()

        if not find_workspace_root():
            raise RuntimeError("workspace root not found!")

        if not os.path.isfile(".torque/local/venv/bin/python"):
            workspace.initialize_venv()

        if os.path.isfile(".torque/local/install_deps"):
            workspace.install_deps()

        pass_through_command(sys.argv[1:], cwd)

        return 0

    except subprocess.CalledProcessError:
        pass

    except RuntimeError as exc:
        print(exc)

    return 1


if __name__ == "__main__":
    sys.exit(main())
