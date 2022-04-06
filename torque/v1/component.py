# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import inspect
import warnings

from abc import ABC
from abc import abstractmethod

from torque.v1 import tao
from torque.v1 import options
from torque.v1 import utils


Artifacts = [str]


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


class Component(ABC):
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 name: str,
                 labels: [str],
                 params: options.Options,
                 config: options.Options):
        # pylint: disable=R0913

        self.name = name
        self.labels = labels
        self.params = params
        self.config = config

        self.artifacts: Artifacts = []
        self.manifest: tao.Manifest = []

        self._inbound_interfaces: dict[str, Interface] = {}
        self._outbound_interfaces: dict[str, Interface] = {}

        for interface in self.inbound_interfaces():
            self._inbound_interfaces[utils.fqcn(interface)] = interface

        for interface in self.outbound_interfaces():
            self._outbound_interfaces[utils.fqcn(interface)] = interface

        self.initialize()

    def inbound_interface(self, cls: type) -> Interface:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._inbound_interfaces:
            return None

        return self._inbound_interfaces[name]

    def outbound_interface(self, cls: type) -> Interface:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._outbound_interfaces:
            return None

        return self._outbound_interfaces[name]

    @staticmethod
    @abstractmethod
    def parameters() -> [options.OptionSpec]:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> [options.OptionSpec]:
        """TODO"""

    @abstractmethod
    def initialize(self):
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
    def on_build(self, deployment: str) -> bool:
        """TODO"""

    @abstractmethod
    def on_generate(self, deployment: str) -> bool:
        """TODO"""
