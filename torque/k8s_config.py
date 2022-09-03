# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes

from torque import v1
from torque import k8s


class KubernetesClient(k8s.KubernetesClientInterface):
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

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""

        return kubernetes.config.new_client_from_config()


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

    def on_apply(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_delete(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_command(self, context: v1.deployment.Context, argv: [str]):
        """TODO"""


repository = {
    "v1": {
        "bonds": {
            "torquetech.io/k8s-config": [
                KubernetesClient
            ]
        },
        "providers": {
            "torquetech.io/k8s-config": Provider
        }
    }
}
