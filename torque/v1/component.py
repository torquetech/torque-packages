# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import inspect
import threading
import warnings

from abc import ABC
from abc import abstractmethod

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


class Component(ABC):
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 name: str,
                 labels: [str],
                 parameters: object,
                 configuration: object,
                 interfaces: object):
        # pylint: disable=R0913

        self.name = name
        self.labels = labels
        self.parameters = parameters
        self.configuration = configuration
        self.interfaces = interfaces

        self._torque_lock = threading.Lock()
        self._torque_interfaces = {}

        for interface in self.on_interfaces():
            if not issubclass(interface.__class__, Interface):
                raise RuntimeError(f"{utils.fqcn(interface)}: invalid interface")

            # pylint: disable=W0212
            interface._torque_lock = self._torque_lock
            cls = interface.__class__

            while cls is not Interface:
                if len(cls.__bases__) != 1:
                    raise RuntimeError(f"{utils.fqcn(cls)}: multiple inheritance not supported")

                fqcn = utils.fqcn(cls)

                if fqcn in self._torque_interfaces:
                    print(f"WARNING: {utils.fqcn(self)}: duplicate interface: {fqcn}")

                self._torque_interfaces[fqcn] = interface
                cls = cls.__bases__[0]

    def _torque_interface(self, cls: type, required: bool) -> Interface:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._torque_interfaces:
            if required:
                raise RuntimeError(f"{self.name}: {name}: component interface not found")

            return None

        return self._torque_interfaces[name]

    @classmethod
    @abstractmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_parameters: not implemented")

    @classmethod
    @abstractmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    @abstractmethod
    def on_requirements(cls) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")

    @abstractmethod
    def on_interfaces(self) -> [Interface]:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_interfaces: not implemented")

    @abstractmethod
    def on_create(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_create: not implemented")

    @abstractmethod
    def on_remove(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_remove: not implemented")

    @abstractmethod
    def on_build(self, deployment: deployment.Deployment):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_build: not implemented")

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_apply: not implemented")
