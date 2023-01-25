# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import argparse
import os
import sys
import traceback

import yaml

from torque import commands
from torque import exceptions
from torque import package
from torque import v1


def fix_pyyaml():
    """DOCSTRING"""

    # Credits for the code in this function:
    # https://stackoverflow.com/a/33300001

    def str_presenter(dumper, data):
        """DOCSTRING"""

        if len(data.splitlines()) > 1:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


def fix_paths():
    """DOCSTRING"""

    if sys.path[0] == os.getcwd():
        sys.path = sys.path[1:]


def main() -> int:
    """DOCSTRING"""

    # For 'python -m module' python always puts in current directory
    # as the first path element and that can mess up the whole environment
    # if the current directory has a file or a directory with the same
    # name as some torque and/or system module. Fix it here until it's
    # fixed upstream.
    fix_paths()

    # Make all yaml.safe_dump() calls check if a string literal
    # is multi-line or not and use '|' style if it is.
    fix_pyyaml()

    argv = sys.argv[1:]
    unparsed_argv = []

    try:
        n = argv.index("--")

        unparsed_argv = argv[n+1:]
        argv = argv[:n]

    except ValueError:
        pass

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
            "component": commands.component,
            "link": commands.link,
            "deployment": commands.deployment,
            "provider": commands.provider,
            "bond": commands.bond,
            "context": commands.context,
            "dag": commands.dag
        }

        for cmd in cmds.values():
            cmd.add_arguments(subparsers)

        args = parser.parse_args(argv)

        cmds[args.main_cmd].run(args, unparsed_argv)

        return 0

    except exceptions.OperationAborted:
        pass

    except exceptions.InternalError as exc:
        if os.getenv("TORQUE_DEBUG"):
            traceback.print_exc()

        print(f"[CRITICAL]: {exc}", file=sys.stderr)

    except v1.exceptions.TorqueException as exc:
        if os.getenv("TORQUE_DEBUG"):
            traceback.print_exc()

        print(exc, file=sys.stderr)

    except package.Exception as exc:
        if os.getenv("TORQUE_DEBUG"):
            traceback.print_exc()

        print(exc, file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
