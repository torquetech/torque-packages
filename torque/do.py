# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1
from torque import dolib


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_apply(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_delete(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_command(self, context: v1.deployment.Context, argv: [str]):
        """TODO"""


repository = {
    "v1": {
        "interfaces": [],
        "providers": {
            "torquetech.io/do": Provider
        }
    }
}
