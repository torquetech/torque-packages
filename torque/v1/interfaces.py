# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import io

from abc import ABC
from abc import abstractmethod

from torque import options


Tags = list[str]
Target = dict[str, object]


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
    def on_build(self):
        """TODO"""


class Link(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 params: options.Options,
                 config: options.Options,
                 source: Component,
                 destination: Component):
        # pylint: disable=R0913

        self.name = name
        self.params = params
        self.config = config
        self.source = source
        self.destination = destination

    @staticmethod
    @abstractmethod
    def parameters() -> options.OptionsSpec:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> options.OptionsSpec:
        """TODO"""

    @abstractmethod
    def on_create(self):
        """TODO"""

    @abstractmethod
    def on_remove(self):
        """TODO"""

    @abstractmethod
    def on_build(self):
        """TODO"""


class Protocol(ABC):
    # pylint: disable=R0903

    """TODO"""

    @staticmethod
    @abstractmethod
    def fetch(uri: str, secret: str) -> io.TextIOWrapper:
        """TODO"""


class DSLInstruction(ABC):
    # pylint: disable=R0903

    """TODO"""


class DSLGenerator(ABC):
    # pylint: disable=R0903

    """TODO"""

    @staticmethod
    @abstractmethod
    def generate(instruction: DSLInstruction) -> Target:
        """TODO"""


class DSL:
    # pylint: disable=R0903

    """TODO"""