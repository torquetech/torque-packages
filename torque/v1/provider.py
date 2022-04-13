# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from abc import ABC
from abc import abstractmethod

from torque import v1


class Provider(ABC):
    """TODO"""

    def __init__(self, configuration: object):
        self.configuration = configuration

        self._lock = threading.Lock()
        self._interfaces: dict[str, v1.interface.Interface] = {}

        for iface in self.interfaces():
            self._interfaces[v1.utils.fqcn(iface)] = iface

    def has_interface(self, cls: type) -> bool:
        """TODO"""

        return v1.utils.fqcn(cls) in self._interfaces

    def interface(self, cls: type) -> v1.interface.Context:
        """TODO"""

        name = v1.utils.fqcn(cls)

        if name not in self._interfaces:
            return v1.interface.Context(self._lock, None)

        return v1.interface.Context(self._lock, self._interfaces[name])

    @staticmethod
    @abstractmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""
