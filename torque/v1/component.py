# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from abc import ABC
from abc import abstractmethod

from . import deployment
from . import interface as interface_v1
from . import utils


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
        self._torque_interfaces = utils.interfaces(self, self._torque_lock, interface_v1.Interface)

    def has_interface(self, cls: type) -> bool:
        """TODO"""

        return utils.fqcn(cls) in self._torque_interfaces

    def interface(self, cls: type) -> interface_v1.Interface:
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
    def interfaces(self) -> [interface_v1.Interface]:
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
