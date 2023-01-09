# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import functools
import inspect
import threading
import types
import warnings

from pprint import pformat

from . import exceptions
from . import deployment
from . import utils


class DummyInterfaceImplementation:
    """DOCSTRING"""

    def __getattribute__(self, attr):
        """DOCSTRING"""

        return None


class Interface:
    """DOCSTRING"""

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


class SourceInterface(Interface):
    """DOCSTRING"""


class DestinationInterface(Interface):
    """DOCSTRING"""


class Component:
    """DOCSTRING"""

    PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self,
                 name: str,
                 parameters: object,
                 configuration: object,
                 context: deployment.Context,
                 interfaces: object):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.configuration = configuration
        self.context = context
        self.interfaces = interfaces

        self._torque_lock = threading.Lock()
        self._torque_interfaces = {}

        for interface in self.on_interfaces():
            if not issubclass(interface.__class__, Interface):
                raise exceptions.RuntimeError(f"{utils.fqcn(interface)}: invalid interface")

            # pylint: disable=W0212
            interface._torque_lock = self._torque_lock
            type = utils.fqcn(interface)

            self._torque_interfaces[type] = interface

    def _torque_interface(self, cls: type, required: bool) -> Interface:
        """DOCSTRING"""

        cls_type = utils.fqcn(cls)

        if cls_type not in self._torque_interfaces:
            if required:
                raise exceptions.RuntimeError(f"{self.name}: {cls_type}: component interface not found")

            return None

        return self._torque_interfaces[cls_type]

    @classmethod
    def describe(cls) -> dict[str, object]:
        """DOCSTRING"""

        bound_interfaces = types.SimpleNamespace()

        for name in cls.on_requirements():
            setattr(bound_interfaces, name, DummyInterfaceImplementation())

        component = cls("internal",
                        cls.PARAMETERS["defaults"],
                        cls.CONFIGURATION["defaults"],
                        deployment.Context("internal", {}),
                        bound_interfaces)

        return {
            "type": utils.fqcn(cls),
            "parameters": {
                "defaults": pformat(cls.PARAMETERS["defaults"]),
                "schema": pformat(cls.PARAMETERS["schema"])
            },
            "configuration": {
                "defaults": pformat(cls.CONFIGURATION["defaults"]),
                "schema": pformat(cls.CONFIGURATION["schema"])
            },
            "interfaces": [
                utils.fqcn(type) for type in component.on_interfaces()
            ],
            "requirements": {
                name: {
                    "interface": utils.fqcn(r["interface"]),
                    "required": r["required"]
                } for name, r in cls.on_requirements().items()
            },
            "description": cls.__doc__
        }

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """DOCSTRING"""

        return utils.validate_schema(cls.PARAMETERS["schema"],
                                     cls.PARAMETERS["defaults"],
                                     parameters)

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

    def on_interfaces(self) -> [Interface]:
        """DOCSTRING"""

        return []

    def on_create(self):
        """DOCSTRING"""

    def on_remove(self):
        """DOCSTRING"""

    def on_build(self):
        """DOCSTRING"""

    def on_apply(self):
        """DOCSTRING"""
