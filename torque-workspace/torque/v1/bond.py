# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from . import deployment
from . import utils


class Interface:
    """DOCSTRING"""


class Bond:
    """DOCSTRING"""

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
    def on_configuration(cls, configuration: object) -> object:
        """DOCSTRING"""

        return utils.validate_schema(cls.CONFIGURATION["schema"],
                                     cls.CONFIGURATION["defaults"],
                                     configuration)

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {}
