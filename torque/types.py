# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC, abstractmethod

from torque import options


class Component(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: options.OptionsSpec = []
    configuration: options.OptionsSpec = []

    @abstractmethod
    def on_build(self):
        """TODO"""


class Link(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: options.OptionsSpec = []
    configuration: options.OptionsSpec = []

    @abstractmethod
    def on_build(self):
        """TODO"""
