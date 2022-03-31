# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from torque.v1 import dsl
from torque.v1 import options


Instructions = list[dsl.Instruction]
Program = dict[str, Instructions]


class Provider(ABC):
    """TODO"""

    def __init__(self, config: options.Options):
        self.config = config

    @staticmethod
    @abstractmethod
    def configuration() -> options.OptionsSpec:
        """TODO"""

    @abstractmethod
    def push(self, artifacts: list[str]):
        """TODO"""

    @abstractmethod
    def apply(self, program: Program, dry_run: bool):
        """TODO"""

    @abstractmethod
    def delete(self, program: Program, dry_run: bool):
        """TODO"""
