# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from torque.v1 import component
from torque.v1 import options
from torque.v1 import tau


class Provider(ABC):
    """TODO"""

    def __init__(self, config: options.Options):
        self.config = config

    @staticmethod
    @abstractmethod
    def configuration() -> [options.OptionSpec]:
        """TODO"""

    @abstractmethod
    def push(self, artifacts: component.Artifacts):
        """TODO"""

    @abstractmethod
    def apply(self, name: str, manifests: tau.Manifests, dry_run: bool):
        """TODO"""

    @abstractmethod
    def delete(self, name: str, dry_run: bool):
        """TODO"""
