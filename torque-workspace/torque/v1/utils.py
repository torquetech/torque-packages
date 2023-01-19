# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import difflib
import inspect
import os
import pathlib
import secrets
import typing
import time

import yaml

from . import exceptions
from . import schema as schema_v1


_SYMBOLS = "0123456789abcdefghijklmnopqrstuvwxyz"
_TORQUE_CWD = None
_TORQUE_ROOT = None


def torque_cwd() -> str:
    # pylint: disable=W0603

    """DOCSTRING"""

    global _TORQUE_CWD

    if _TORQUE_CWD:
        return _TORQUE_CWD

    _TORQUE_CWD = os.getenv("PWD", os.getcwd())

    return _TORQUE_CWD


def torque_root() -> str:
    # pylint: disable=W0603

    """DOCSTRING"""

    global _TORQUE_ROOT

    if _TORQUE_ROOT:
        return _TORQUE_ROOT

    cwd = pathlib.Path(torque_cwd())

    while True:
        if os.path.isdir(f"{cwd}/.torque"):
            break

        if cwd.parent == cwd:
            raise exceptions.RuntimeError("workspace root not found!")

        cwd = cwd.parent

    _TORQUE_ROOT = str(cwd)

    return _TORQUE_ROOT


def torque_path(path: str) -> str:
    """DOCSTRING"""

    if os.path.isabs(path):
        return path

    root = torque_root()

    path = f"{torque_cwd()}/{path}"
    path = os.path.normpath(path)
    path = os.path.relpath(path, root)

    return path


def torque_dir() -> str:
    """DOCSTRING"""

    return f"{torque_root()}/.torque"


def resolve_path(path: str) -> str:
    """DOCSTRING"""

    if os.path.isabs(path):
        return path

    path = f"{torque_root()}/{path}"
    path = os.path.normpath(path)

    return path


def fqcn(obj: object) -> str:
    """DOCSTRING"""

    if not inspect.isclass(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"

    return f"{obj.__module__}.{obj.__name__}"


def merge_dicts(dict1: dict[str, object],
                dict2: dict[str, object],
                allow_overwrites: bool = True) -> dict[str, object]:
    """DOCSTRING"""

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
                    raise exceptions.RuntimeError(f"{key}: duplicate entry")

            new_dict[key] = dict2[key]

    return new_dict


def validate_schema(schema: object, defaults: object, instance: object) -> object:
    """DOCSTRING"""

    return schema_v1.Schema(schema).validate(merge_dicts(defaults, instance))


T = typing.TypeVar("T")


class Future(typing.Generic[T]):
    """DOCSTRING"""

    def __init__(self, obj: object, *args, **kwargs):
        self._obj = obj
        self._args = args
        self._kwargs = kwargs

        self._cached_value = None

    def __call__(self):
        if self._cached_value:
            return self._cached_value

        if callable(self._obj):
            self._cached_value = self._obj(*self._args, **self._kwargs)

        else:
            self._cached_value = self._obj

        return self._cached_value


def resolve_futures(obj: object) -> object:
    """DOCSTRING"""

    if isinstance(obj, dict):
        return {
            k: resolve_futures(v) for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            resolve_futures(v) for v in obj
        ]

    if isinstance(obj, Future):
        return resolve_futures(obj())

    return obj


def diff_objects(name: str, obj1: dict[str, object], obj2: dict[str, object]):
    """DOCSTRING"""

    obj1 = yaml.safe_dump(obj1,
                          default_flow_style=False,
                          sort_keys=False) if obj1 else ""

    obj2 = yaml.safe_dump(obj2,
                          default_flow_style=False,
                          sort_keys=False) if obj2 else ""

    diff = difflib.unified_diff(obj1.split("\n"),
                                obj2.split("\n"),
                                fromfile=f"a/{name}",
                                tofile=f"b/{name}",
                                lineterm="")

    return "\n".join(diff)


def apply_objects(current_state: dict[str, object],
                  new_state: dict[str, object],
                  update_fn: typing.Callable,
                  delete_fn: typing.Callable):
    """DOCSTRING"""

    for name in list(new_state.keys()):
        update_fn(name)

    for name in list(current_state.keys()):
        if name in new_state:
            continue

        delete_fn(name)


def wait_for(cond_fn: typing.Callable, message: str, interval: int = 10):
    """DOCSTRING"""

    if cond_fn():
        return

    last_ts = time.time()
    ndx = 0

    while True:
        if ndx == 4:
            blanks = " " * (ndx + len(message))
            print(f"\r{blanks}\r{message}", end="", flush=True)

            ndx = 1

        else:
            dots = "." * ndx
            print(f"\r{message}{dots}", end="", flush=True)

            ndx += 1

        time.sleep(1)

        if (time.time() - last_ts) >= interval:
            if cond_fn():
                break

            last_ts = time.time()

    if ndx != 0:
        print("." * (4 - ndx), flush=True)


def random_suffix(length: int):
    """DOCSTRING"""

    return ''.join([_SYMBOLS[i % len(_SYMBOLS)]
                    for i in secrets.token_bytes(length)])
