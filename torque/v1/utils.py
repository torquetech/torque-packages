# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import inspect
import os
import pathlib
import threading


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


def fqcn(obj: object) -> str:
    """TODO"""

    if not inspect.isclass(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"

    return f"{obj.__module__}.{obj.__name__}"


def merge_dicts(dict1: dict[str, object],
                dict2: dict[str, object],
                allow_overwrites: bool = True) -> dict[str, object]:
    """TODO"""

    new_dict = {} | dict1

    for key in dict2.keys():
        if isinstance(dict2[key], dict):
            if key in new_dict:
                new_dict[key] = merge_dicts(new_dict[key],
                                            dict2[key],
                                            allow_overwrites)

            else:
                new_dict[key] = dict2[key]

        else:
            if not allow_overwrites:
                if key in new_dict:
                    raise RuntimeError(f"{key}: duplicate entry")

            new_dict[key] = dict2[key]

    return new_dict


def interfaces(instance: object,
               lock: threading.Lock,
               interface_type: type) -> dict[str, object]:
    """TODO"""

    interfaces = {}

    for iface in instance.interfaces():
        if not issubclass(iface.__class__, interface_type):
            raise RuntimeError(f"{fqcn(iface)}: invalid interface")

        # pylint: disable=W0212
        iface._torque_lock = lock
        cls = iface.__class__

        while cls is not interface_type:
            interfaces[fqcn(cls)] = iface
            cls = cls.__bases__[0]

    return interfaces
