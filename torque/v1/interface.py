# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import inspect
import threading
import typing
import warnings

from . import utils


T = typing.TypeVar("T")


class Interface:
    """TODO"""

    def __init__(self, **kwargs):
        self._torque_lock: threading.Lock = None

        required_funcs = inspect.getmembers(self, predicate=inspect.ismethod)
        required_funcs = filter(lambda x: not x[0].startswith("_"), required_funcs)
        required_funcs = set(map(lambda x: x[0], required_funcs))

        provided_funcs = set(kwargs.keys())

        if required_funcs - provided_funcs:
            funcs = ", ".join(list(required_funcs - provided_funcs))
            raise NotImplementedError(f"{utils.fqcn(self)}: {funcs}: not implemented")

        if provided_funcs - required_funcs:
            warnings.warn("extra methods provided", stacklevel=2)

        for name, func in kwargs.items():
            setattr(self, name, functools.partial(self._torque_call_wrapper, func))

    def _torque_call_wrapper(self, func, *args, **kwargs):
        # pylint: disable=E1129
        with self._torque_lock:
            return func(*args, **kwargs)


class Future(typing.Generic[T]):
    """TODO"""

    def __init__(self, value=None):
        self._condition = threading.Condition()
        self._value = value

    def get(self):
        """TODO"""

        with self._condition:
            while self._value is None:
                self._condition.wait()

            return self._value

    def set(self, value: object):
        """TODO"""

        with self._condition:
            assert self._value is None

            self._value = value
            self._condition.notify_all()
