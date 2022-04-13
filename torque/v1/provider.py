# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod


class Provider(ABC):
    """TODO"""

    def __init__(self, configuration: object):
        self.configuration = configuration

    @staticmethod
    @abstractmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""
