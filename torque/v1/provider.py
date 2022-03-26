# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from torque.v1 import dsl
from torque.v1 import options


Target = dict[str, object]
Targets = dict[str, Target]

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
    def compile(self, program: Program) -> Targets:
        """TODO"""

    @abstractmethod
    def apply(self, targets: Targets):
        """TODO"""
