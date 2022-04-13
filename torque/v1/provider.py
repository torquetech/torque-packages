# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from abc import ABC
from abc import abstractmethod

from torque.v1 import interface as interface_v1
from torque.v1 import utils as utils_v1


class Provider(ABC):
    """TODO"""

    def __init__(self, configuration: object):
        self.configuration = configuration

        self._lock = threading.Lock()
        self._interfaces: dict[str, v1_interface.Interface] = {}

        for iface in self.interfaces():
            self._interfaces[utils_v1.fqcn(iface)] = iface

    def has_interface(self, cls: type) -> bool:
        """TODO"""

        return utils_v1.fqcn(cls) in self._interfaces

    def interface(self, cls: type) -> interface_v1.Context:
        """TODO"""

        name = utils_v1.fqcn(cls)

        if name not in self._interfaces:
            return interface_v1.Context(self._lock, None)

        return interface_v1.Context(self._lock, self._interfaces[name])

    @staticmethod
    @abstractmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def interfaces(self) -> [interface_v1.Interface]:
        """TODO"""

