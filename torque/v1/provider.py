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


class Provider(ABC):
    """TODO"""

    def __init__(self, configuration: object):
        self.configuration = configuration

        self._torque_lock = threading.Lock()
        self._torque_interfaces = utils.interfaces(self,
                                                   self._torque_lock,
                                                   interface_v1.Interface)

    def has_interface(self, cls: type) -> bool:
        """TODO"""

        return utils.fqcn(cls) in self._torque_interfaces

    def interface(self, cls: type) -> interface_v1.Interface:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._torque_interfaces:
            raise RuntimeError(f"{name}: provider interface not found")

        return self._torque_interfaces[name]

    @classmethod
    @abstractmethod
    def validate_configuration(cls, configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def interfaces(self) -> [interface_v1.Interface]:
        """TODO"""

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment):
        """TODO"""
