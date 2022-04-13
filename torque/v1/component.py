# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import inspect
import threading
import warnings

from abc import ABC
from abc import abstractmethod

from torque.v1 import build
from torque.v1 import deployment
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


class InterfaceContext:
    """TODO"""

    def __init__(self, lock: threading.Lock, interface: Interface):
        self._lock = lock
        self._interface = interface

    def __enter__(self):
        self._lock.acquire()
        return self._interface

    def __exit__(self, type, value, traceback):
        self._lock.release()


class Component(ABC):
    # pylint: disable=R0902

    """TODO"""

    def __init__(self, name: str, labels: [str], parameters: object, configuration: object):
        # pylint: disable=R0913

        self.name = name
        self.labels = labels
        self.parameters = parameters
        self.configuration = configuration

        self.artifacts: [str] = []

        self._inbound_interfaces: dict[str, Interface] = {}
        self._outbound_interfaces: dict[str, Interface] = {}

        for interface in self.inbound_interfaces():
            self._inbound_interfaces[utils.fqcn(interface)] = interface

        for interface in self.outbound_interfaces():
            self._outbound_interfaces[utils.fqcn(interface)] = interface

        self._lock = threading.Lock()

    def inbound_interface(self, cls: type) -> InterfaceContext:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._inbound_interfaces:
            return InterfaceContext(self._lock, None)

        return InterfaceContext(self._lock, self._inbound_interfaces[name])

    def outbound_interface(self, cls: type) -> InterfaceContext:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._outbound_interfaces:
            return InterfaceContext(self._lock, None)

        return InterfaceContext(self._lock, self._outbound_interfaces[name])

    @staticmethod
    @abstractmethod
    def validate_parameters(parameters: object) -> object:
        """TODO"""

    @staticmethod
    @abstractmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def inbound_interfaces(self) -> [Interface]:
        """TODO"""

    @abstractmethod
    def outbound_interfaces(self) -> [Interface]:
        """TODO"""

    @abstractmethod
    def on_create(self):
        """TODO"""

    @abstractmethod
    def on_remove(self):
        """TODO"""

    @abstractmethod
    def on_build(self, build: build.Build) -> bool:
        """TODO"""

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment) -> bool:
        """TODO"""
