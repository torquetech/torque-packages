# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import inspect
import threading
import warnings

from torque.v1 import utils


class Interface:
    """TODO"""

    def __init__(self, **kwargs):
        required_funcs = inspect.getmembers(self, predicate=inspect.ismethod)
        required_funcs = filter(lambda x: not x[0].startswith("_"), required_funcs)
        required_funcs = set(map(lambda x: x[0], required_funcs))

        provided_funcs = set(kwargs.keys())

        if required_funcs - provided_funcs:
            raise NotImplementedError(utils.fqcn(self))

        if provided_funcs - required_funcs:
            warnings.warn("extra methods provided", stacklevel=2)

        for name, func in kwargs.items():
            setattr(self, name, func)


class Context:
    """TODO"""

    def __init__(self, lock: threading.Lock, interface: Interface):
        self._lock = lock
        self._interface = interface

    def __enter__(self):
        self._lock.acquire()
        return self._interface

    def __exit__(self, type, value, traceback):
        self._lock.release()
