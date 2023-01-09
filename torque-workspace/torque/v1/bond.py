# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from pprint import pformat

from . import deployment
from . import utils


class Interface:
    """DOCSTRING"""


class Bond:
    """DOCSTRING"""

    PROVIDER = None
    IMPLEMENTS = None

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self,
                 name: str,
                 configuration: object,
                 context: deployment.Context,
                 interfaces: object):
        self.name = name
        self.configuration = configuration
        self.context = context
        self.interfaces = interfaces

    @classmethod
    def describe(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "type": utils.fqcn(cls),
            "provider": utils.fqcn(cls.PROVIDER),
            "implements": utils.fqcn(cls.IMPLEMENTS),
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
    def on_configuration(cls, configuration: object) -> object:
        """DOCSTRING"""

        return utils.validate_schema(cls.CONFIGURATION["schema"],
                                     cls.CONFIGURATION["defaults"],
                                     configuration)

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {}
