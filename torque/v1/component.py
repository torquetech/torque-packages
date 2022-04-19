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
        # pylint: disable=E1129,W0212

        with self._torque_lock:
            return func(*args, **kwargs)


class Component(ABC):
    # pylint: disable=R0902

    """TODO"""

    def __init__(self, name: str, labels: [str], parameters: object, configuration: object):
        # pylint: disable=R0913

        self.name = name
        self.labels = labels
        self.parameters = parameters
        self.configuration = configuration

        self._torque_lock = threading.Lock()
        self._torque_interfaces = {}

        for iface in self.interfaces():
            if not issubclass(iface.__class__, Interface):
                raise RuntimeError(f"{utils.fqcn(iface)}: invalid interface")

            # pylint: disable=W0212
            iface._torque_lock = self._torque_lock
            cls = iface.__class__

            while cls is not Interface:
                self._torque_interfaces[utils.fqcn(cls)] = iface
                cls = cls.__bases__[0]

    def has_interface(self, cls: type) -> bool:
        """TODO"""

        return utils.fqcn(cls) in self._torque_interfaces

    def interface(self, cls: type) -> Interface:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._torque_interfaces:
            raise RuntimeError(f"{name}: interface not found")

        return self._torque_interfaces[name]

    @classmethod
    @abstractmethod
    def validate_parameters(cls, parameters: object) -> object:
        """TODO"""

    @classmethod
    @abstractmethod
    def validate_configuration(cls, configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def interfaces(self) -> [Interface]:
        """TODO"""

    @abstractmethod
    def on_create(self):
        """TODO"""

    @abstractmethod
    def on_remove(self):
        """TODO"""

    @abstractmethod
    def on_build(self, deployment: deployment.Deployment) -> bool:
        """TODO"""

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment) -> bool:
        """TODO"""
