# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from abc import ABC
from abc import abstractmethod

from torque.v1 import build
from torque.v1 import deployment
from torque.v1 import interface
from torque.v1 import utils


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

        self._inbound_interfaces: dict[str, interface.Interface] = {}
        self._outbound_interfaces: dict[str, interface.Interface] = {}

        for iface in self.inbound_interfaces():
            self._inbound_interfaces[utils.fqcn(iface)] = iface

        for iface in self.outbound_interfaces():
            self._outbound_interfaces[utils.fqcn(iface)] = iface

        self._lock = threading.Lock()

    def inbound_interface(self, cls: type) -> interface.Context:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._inbound_interfaces:
            return interface.Context(self._lock, None)

        return interface.Context(self._lock, self._inbound_interfaces[name])

    def outbound_interface(self, cls: type) -> interface.Context:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._outbound_interfaces:
            return interface.Context(self._lock, None)

        return interface.Context(self._lock, self._outbound_interfaces[name])

    @staticmethod
    @abstractmethod
    def validate_parameters(parameters: object) -> object:
        """TODO"""

    @staticmethod
    @abstractmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def inbound_interfaces(self) -> [interface.Interface]:
        """TODO"""

    @abstractmethod
    def outbound_interfaces(self) -> [interface.Interface]:
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
