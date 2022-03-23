# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import io

from abc import ABC
from abc import abstractmethod
from collections import namedtuple


Options = dict[str, str]

OptionSpec = namedtuple("OptionSpec", ["name", "description", "default_value", "process_fn"])
OptionsSpec = list[OptionSpec]

Tags = list[str]
Target = dict[str, object]


class Component(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 group: str,
                 params: Options,
                 config: Options):
        self.name = name
        self.group = group
        self.params = params
        self.config = config

    @staticmethod
    @abstractmethod
    def parameters() -> OptionsSpec:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> OptionsSpec:
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
                 params: Options,
                 config: Options,
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
    def parameters() -> OptionsSpec:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> OptionsSpec:
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
    """TODO"""

    @staticmethod
    @abstractmethod
    def fetch(uri: str, secret: str) -> io.TextIOWrapper:
        """TODO"""


class DSLInstruction(ABC):
    """TODO"""


class DSLGenerator(ABC):
    """TODO"""

    @staticmethod
    @abstractmethod
    def generate(instruction: DSLInstruction) -> Target:
        """TODO"""


class DSL:
    """TODO"""
