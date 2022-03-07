# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple
from abc import ABC, abstractmethod


Parameter = namedtuple("Parameter", ["name", "description", "default_value"])
Option = namedtuple("Option", ["name", "description", "default_value"])


class Component(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: list[Parameter] = []
    configuration: list[Option] = []

    @abstractmethod
    def on_build(self):
        """TODO"""


class Link(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: list[Parameter] = []
    configuration: list[Option] = []

    @abstractmethod
    def on_build(self):
        """TODO"""
