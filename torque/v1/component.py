# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from torque.v1 import tao
from torque.v1 import options


Artifacts = [str]
Tags = [str]


class Component(ABC):
    """TODO"""

    def __init__(self,
                 name: str,
                 labels: [str],
                 params: options.Options,
                 config: options.Options):
        # pylint: disable=R0913

        self.name = name
        self.labels = labels
        self.params = params
        self.config = config

        self.artifacts: Artifacts = []
        self.manifest: tao.Manifest = []

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
    def on_build(self) -> bool:
        """TODO"""

    @abstractmethod
    def on_generate(self) -> bool:
        """TODO"""
