# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from . import component
from . import deployment


class Link(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 parameters: object,
                 configuration: object,
                 source: component.Component,
                 destination: component.Component):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.configuration = configuration
        self.source = source
        self.destination = destination

    @classmethod
    @abstractmethod
    def parameters(cls, parameters: object) -> object:
        """TODO"""

    @classmethod
    @abstractmethod
    def configuration(cls, configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def on_create(self):
        """TODO"""

    @abstractmethod
    def on_remove(self):
        """TODO"""

    @abstractmethod
    def on_build(self, deployment: deployment.Deployment):
        """TODO"""

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment):
        """TODO"""
