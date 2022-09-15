# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes

from torque import v1
from torque import k8s


class Provider(v1.provider.Provider):
    """TODO"""


class KubernetesClient(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = k8s.KubernetesClientInterface

    _CONFIGURATION = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("config_file"): str,
            v1.schema.Optional("context"): str
        }
    }

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""

        return kubernetes.config.new_client_from_config(self.configuration.get("config_file"),
                                                        self.configuration.get("context"))


repository = {
    "v1": {
        "providers": [
            Provider
        ],
        "bonds": [
            KubernetesClient
        ]
    }
}
