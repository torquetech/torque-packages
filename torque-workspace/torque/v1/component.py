# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import inspect
import threading
import warnings

from . import exceptions
from . import deployment
from . import utils


class Interface:
    """TODO"""

    def __init__(self, **kwargs):
        self._torque_lock = None

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


class Component:
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self,
                 name: str,
                 parameters: dict[str, object],
                 configuration: dict[str, object],
                 context: deployment.Context,
                 bonds: object):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.configuration = configuration
        self.context = context
        self.bonds = bonds

        self._torque_lock = threading.Lock()
        self._torque_interfaces = {}

        for interface in self.on_interfaces():
            if not issubclass(interface.__class__, Interface):
                raise exceptions.RuntimeError(f"{utils.fqcn(interface)}: invalid interface")

            # pylint: disable=W0212
            interface._torque_lock = self._torque_lock
            cls = interface.__class__

            while cls is not Interface:
                cls_type = utils.fqcn(cls)

                if len(cls.__bases__) != 1:
                    raise exceptions.RuntimeError(f"{cls_type}: multiple inheritance not supported")

                if cls_type in self._torque_interfaces:
                    print(f"WARNING: {utils.fqcn(self)}: duplicate interface: {cls_type}")

                self._torque_interfaces[cls_type] = interface
                cls = cls.__bases__[0]

    def _torque_interface(self, cls: type, required: bool) -> Interface:
        """TODO"""

        cls_type = utils.fqcn(cls)

        if cls_type not in self._torque_interfaces:
            if required:
                raise exceptions.RuntimeError(f"{self.name}: {cls_type}: component interface not found")

            return None

        return self._torque_interfaces[cls_type]

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        return utils.validate_schema(cls._PARAMETERS["schema"],
                                     cls._PARAMETERS["defaults"],
                                     parameters)

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return utils.validate_schema(cls._CONFIGURATION["schema"],
                                     cls._CONFIGURATION["defaults"],
                                     configuration)

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {}

    def on_interfaces(self) -> [Interface]:
        """TODO"""

        return []

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self):
        """TODO"""

    def on_apply(self):
        """TODO"""
