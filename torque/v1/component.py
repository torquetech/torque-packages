# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from torque.v1 import tao
from torque.v1 import options


Tags = list[str]


class Component(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 group: str,
                 params: options.Options,
                 config: options.Options):
        self.name = name
        self.group = group
        self.params = params
        self.config = config

    @staticmethod
    @abstractmethod
    def parameters() -> options.OptionsSpec:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> options.OptionsSpec:
        """TODO"""

    @abstractmethod
    def inbound_tags(self) -> Tags:
        """TODO"""

    @abstractmethod
    def outbound_tags(self) -> Tags:
        """TODO"""

    @abstractmethod
    def on_create(self):
        """TODO"""

    @abstractmethod
    def on_remove(self):
        """TODO"""

    @abstractmethod
    def on_build(self) -> list[str]:
        """TODO"""

    @abstractmethod
    def on_generate(self) -> list[tao.Instruction]:
        """TODO"""
