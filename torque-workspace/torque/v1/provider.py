# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import inspect
import threading
import typing

from pprint import pformat

from . import deployment
from . import utils


class _ProviderContext:
    """DOCSTRING"""

    def __init__(self,
                 data: dict[str, object],
                 hooks: list[typing.Callable]):
        self._data = data
        self._hooks = hooks

    def set_data(self, cls: type, name: str, data: object):
        """DOCSTRING"""

        cls_type = utils.fqcn(cls)

        if cls_type not in self._data:
            self._data[cls_type] = {}

        self._data[cls_type][name] = data

    def get_data(self, cls: type, name: str) -> object:
        """DOCSTRING"""

        cls_type = utils.fqcn(cls)

        if cls_type not in self._data:
            return None

        return self._data[cls_type].get(name)

    def add_hook(self, bucket: str, hook: typing.Callable):
        """DOCSTRING"""

        assert callable(hook)

        if bucket not in self._hooks:
            self._hooks[bucket] = []

        self._hooks[bucket].append(hook)


class Provider:
    """DOCSTRING"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self,
                 configuration: object,
                 context: deployment.Context,
                 interfaces: object):
        self.configuration = configuration
        self.context = context
        self.interfaces = interfaces

        self._lock = threading.Lock()
        self._data = {}
        self._hooks = {}

    def __enter__(self):
        self._lock.acquire()

        return _ProviderContext(self._data, self._hooks)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    @classmethod
    def describe(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "type": utils.fqcn(cls),
            "configuration": {
                "defaults": pformat(cls.CONFIGURATION["defaults"]),
                "schema": pformat(cls.CONFIGURATION["schema"])
            },
            "requirements": {
                name: {
                    "interface": utils.fqcn(r["interface"]),
                    "required": r["required"]
                } for name, r in cls.on_requirements().items()
            },
            "description": cls.__doc__
        }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """DOCSTRING"""

        return utils.validate_schema(cls.CONFIGURATION["schema"],
                                     cls.CONFIGURATION["defaults"],
                                     configuration)

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {}

    def run_hooks(self, bucket: str, **kwargs):
        """DOCSTRING"""

        quiet = kwargs.get("quiet", True)
        reverse = kwargs.get("reverse", False)
        op = kwargs.get("op", bucket)

        hooks = self._hooks.get(bucket, [])

        if reverse:
            hooks = reversed(hooks)

        for hook in hooks:
            if not quiet:
                if inspect.isfunction(hook):
                    name = f"{hook.__module__}.{hook.__qualname__}"

                elif inspect.ismethod(hook):
                    name = utils.fqcn(hook.__self__)

                else:
                    name = utils.fqcn(hook)

                print(f"{op} {name}...")

            hook()
