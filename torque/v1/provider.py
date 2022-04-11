# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod
from collections import namedtuple

from torque.v1 import options


Manifest = namedtuple("Manifest", [
    "type",
    "name",
    "labels",
    "statements"
])


class Provider(ABC):
    """TODO"""

    def __init__(self, config: options.Options):
        self.config = config

    @staticmethod
    @abstractmethod
    def configuration() -> [options.OptionSpec]:
        """TODO"""

    @abstractmethod
    def push(self, artifacts: [str]):
        """TODO"""

    @abstractmethod
    def apply(self, name: str, manifests: [Manifest], dry_run: bool):
        """TODO"""

    @abstractmethod
    def delete(self, name: str, dry_run: bool):
        """TODO"""
