# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from . import deployment
from . import utils


class Link:
    """DOCSTRING"""

    PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self,
                 name: str,
                 parameters: object,
                 configuration: object,
                 context: deployment.Context,
                 source: str,
                 destination: str,
                 interfaces: object):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.configuration = configuration
        self.context = context
        self.source = source
        self.destination = destination
        self.interfaces = interfaces

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """DOCSTRING"""

        return utils.validate_schema(cls.PARAMETERS["schema"],
                                     cls.PARAMETERS["defaults"],
                                     parameters)

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """DOCSTRING"""

        return utils.validate_schema(cls.CONFIGURATION["schema"],
                                     cls.CONFIGURATION["defaults"],
                                     configuration)

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {}

    def on_create(self):
        """DOCSTRING"""

    def on_remove(self):
        """DOCSTRING"""

    def on_build(self):
        """DOCSTRING"""

    def on_apply(self):
        """DOCSTRING"""
