# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import pathlib
import os
import subprocess
import sys

from torque import init
from torque import workspace


class InvalidWorkspace(Exception):
    """DOCSTRING"""


def torque_cwd() -> str:
    """DOCSTRING"""

    return os.getenv("PWD", os.getcwd())


def torque_root() -> str:
    """DOCSTRING"""

    cwd = pathlib.Path(torque_cwd())

    while True:
        if os.path.isdir(f"{cwd}/.torque"):
            break

        if cwd.parent == cwd:
            return None

        cwd = cwd.parent

    return str(cwd)


def pass_through_command(root: str, argv):
    """DOCSTRING"""

    hook = os.getenv("TORQUE_HOOK", "torque.hooks.main")

    cmd = [
        f"{root}/.torque/local/venv/bin/python",
        "-m", hook
    ]

    cmd += argv

    env = os.environ | {
        "VIRTUAL_ENV": f"{root}/.torque/local/venv"
    }

    subprocess.run(cmd, env=env, check=True)


def main() -> int:
    """DOCSTRING"""

    # pylint: disable=W0703
    try:
        root = torque_root()

        if len(sys.argv) > 1:
            parser = argparse.ArgumentParser(description="torque command line interface.")
            subparsers = parser.add_subparsers(required=True,
                                               dest="main_cmd",
                                               metavar="command")

            init.add_arguments(subparsers)

            if sys.argv[1] == "init":
                init.run(torque_cwd(), parser.parse_args())

                return 0

            if not root and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
                parser.parse_args()

        if root:
            if not os.path.isfile(f"{root}/.torque/local/venv/bin/python"):
                workspace.initialize_venv(root)
                workspace.install_deps(root)

            pass_through_command(root, sys.argv[1:])

        else:
            raise RuntimeError("workspace root not found!")

        return 0

    except subprocess.CalledProcessError:
        pass

    except RuntimeError as exc:
        print(exc)

    return 1


if __name__ == "__main__":
    sys.exit(main())
