# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from . import deployment
from . import utils


class Link(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 parameters: dict,
                 configuration: dict,
                 interfaces: object,
                 source: str,
                 destination: str):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.configuration = configuration
        self.interfaces = interfaces
        self.source = source
        self.destination = destination

    @classmethod
    @abstractmethod
    def on_parameters(cls, parameters: dict) -> dict:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_parameters: not implemented")

    @classmethod
    @abstractmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    @abstractmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")

    @abstractmethod
    def on_create(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_create: not implemented")

    @abstractmethod
    def on_remove(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_remove: not implemented")

    @abstractmethod
    def on_build(self, deployment: deployment.Deployment):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_build: not implemented")

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_apply: not implemented")
