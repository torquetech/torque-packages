# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading
import typing

from . import deployment
from . import utils


class _Provider:
    """TODO"""
    def __init__(self, data, pre_apply_hooks, post_apply_hooks):
        self._data = data
        self._pre_apply_hooks = pre_apply_hooks
        self._post_apply_hooks = post_apply_hooks

    def set_data(self, cls: type, name: str, data: object):
        """TODO"""

        cls = utils.fqcn(cls)

        if cls not in self._data:
            self._data[cls] = {}

        self._data[cls][name] = data

    def get_data(self, cls: type, name: str) -> object:
        """TODO"""

        cls = utils.fqcn(cls)

        if cls not in self._data:
            return None

        return self._data[cls].get(name)

    def add_pre_apply_hook(self, hook: typing.Callable):
        """TODO"""

        self._pre_apply_hooks.append(hook)

    def add_post_apply_hook(self, hook: typing.Callable):
        """TODO"""

        self._post_apply_hooks.append(hook)


class Provider:
    """TODO"""

    def __init__(self,
                 parameters: dict,
                 configuration: dict,
                 context: deployment.Context,
                 bonds: object):
        self.parameters = parameters
        self.configuration = configuration
        self.context = context
        self.bonds = bonds

        self._lock = threading.Lock()
        self._data = {}
        self._pre_apply_hooks = []
        self._post_apply_hooks = []

    def __enter__(self):
        self._lock.acquire()

        return _Provider(self._data, self._pre_apply_hooks, self._post_apply_hooks)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    def apply(self):
        """TODO"""

        for hook in self._pre_apply_hooks:
            hook()

        self.on_apply()

        for hook in self._post_apply_hooks:
            hook()

    def delete(self):
        """TODO"""

        self.on_delete()

    def command(self, argv: [str]):
        """TODO"""

        self.on_command(argv)

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")

    def on_apply(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_apply: not implemented")

    def on_delete(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_delete: not implemented")

    def on_command(self, argv: [str]):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_command: not implemented")
