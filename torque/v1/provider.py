# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from . import deployment
from . import utils


class Provider(ABC):
    """TODO"""

    def __init__(self, configuration: object):
        self.configuration = configuration

    @classmethod
    @abstractmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @abstractmethod
    def on_apply(self, deployment: deployment.Deployment):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_apply: not implemented")

    @abstractmethod
    def on_delete(self, deployment: deployment.Deployment):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_delete: not implemented")


class Interface:
    """TODO"""

    def __init__(self, configuration: object, provider: Provider, labels: [str]):
        self.configuration = configuration
        self.provider = provider
        self.labels = labels

    @classmethod
    @abstractmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""
