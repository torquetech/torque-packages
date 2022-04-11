# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import inspect
import os
import pathlib


_TORQUE_CWD = None
_TORQUE_ROOT = None


def torque_cwd() -> str:
    # pylint: disable=W0603

    """TODO"""

    global _TORQUE_CWD

    if _TORQUE_CWD:
        return _TORQUE_CWD

    _TORQUE_CWD = os.getenv("PWD", os.getcwd())

    return _TORQUE_CWD


def torque_root() -> str:
    # pylint: disable=W0603

    """TODO"""

    global _TORQUE_ROOT

    if _TORQUE_ROOT:
        return _TORQUE_ROOT

    cwd = pathlib.Path(torque_cwd())

    while True:
        if os.path.isdir(f"{cwd}/.torque"):
            break

        if cwd.parent == cwd:
            raise RuntimeError("workspace root not found!")

        cwd = cwd.parent

    _TORQUE_ROOT = str(cwd)

    return _TORQUE_ROOT


def torque_path(path: str) -> str:
    """TODO"""

    if os.path.isabs(path):
        return path

    root = torque_root()

    path = f"{torque_cwd()}/{path}"
    path = os.path.normpath(path)
    path = os.path.relpath(path, root)

    return path


def torque_dir() -> str:
    """TODO"""

    return f"{torque_root()}/.torque"


def resolve_path(path: str) -> str:
    """TODO"""

    if os.path.isabs(path):
        return path

    path = f"{torque_root()}/{path}"
    path = os.path.normpath(path)

    return path


def fqcn(instance: object) -> str:
    """TODO"""

    if not inspect.isclass(instance):
        return f"{instance.__class__.__module__}.{instance.__class__.__name__}"

    return f"{instance.__module__}.{instance.__name__}"
