# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from pprint import pformat

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
    def describe(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "type": utils.fqcn(cls),
            "parameters": {
                "defaults": pformat(cls.PARAMETERS["defaults"]),
                "schema": pformat(cls.PARAMETERS["schema"])
            },
            "configuration": {
                "defaults": pformat(cls.CONFIGURATION["defaults"]),
                "schema": pformat(cls.CONFIGURATION["schema"])
            },
            "requirements": {
                name: {
                    "interface": utils.fqcn(r["interface"]),
                    "required": r["required"]
                } for name, r in cls.on_requirements().items()
            },
            "description": cls.__doc__
        }

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
