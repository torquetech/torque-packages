# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from torque.v1 import component
from torque.v1 import tau


class Link(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 parameters: object,
                 source: component.Component,
                 destination: component.Component):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.source = source
        self.destination = destination
        self.configuration = None

        self.artifacts: [str] = []
        self.statements: [tau.Statement] = []

    @staticmethod
    @abstractmethod
    def validate_parameters(parameters: object) -> object:
        """TODO"""

    @staticmethod
    @abstractmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def on_create(self):
        """TODO"""

    @abstractmethod
    def on_remove(self):
        """TODO"""

    @abstractmethod
    def on_initialize(self, configuration: object):
        """TODO"""

    @abstractmethod
    def on_build(self, deployment: str, profile: str) -> bool:
        """TODO"""

    @abstractmethod
    def on_generate(self, deployment: str, profile: str) -> bool:
        """TODO"""
