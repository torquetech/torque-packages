# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from torque import v1

from demo import providers


class EBSProvider(providers.EBSProvider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self, name: str, size: int) -> v1.utils.Future[str]:
        """TODO"""

        return v1.utils.Future(f"<volume_id_for_{name}_{size}>")


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._lock = threading.Lock()

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_delete(self, deployment: str):
        """TODO"""
