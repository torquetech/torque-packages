# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC
from abc import abstractmethod

from . import metadata


class Provider(ABC):
    """TODO"""

    def __init__(self, metadata: metadata.Deployment, configuration: object):
        self.metadata = metadata
        self.configuration = configuration

    @classmethod
    @abstractmethod
    def validate_configuration(cls, configuration: object) -> object:
        """TODO"""

    @abstractmethod
    def on_apply(self):
        """TODO"""
