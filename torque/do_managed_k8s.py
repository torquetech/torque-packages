# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes

from torque import v1
from torque import k8s
from torque import dolib


class KubernetesClient(k8s.KubernetesClientInterface):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "version": "latest",
            "node_pools": [{
                "size": "s-1vcpu-2gb",
                "name": "pool-1",
                "count": 2
            }]
        },
        "schema": {
            "version": str,
            "node_pools": [{
                "size": str,
                "name": str,
                "count": int,
                v1.schema.Optional("tags"): [str],
                v1.schema.Optional("labels"): v1.schema.Or(None, {
                    v1.schema.Optional(str): str
                }),
                v1.schema.Optional("taints"): [{
                    "key": str,
                    "value": str,
                    "effect": v1.schema.Or("NoSchedule",
                                           "PreferNoSchedule",
                                           "NoExecute")
                }],
                v1.schema.Optional("auto_scale"): bool,
                v1.schema.Optional("min_nodes"): int,
                v1.schema.Optional("max_nodes"): int
            }],
            v1.schema.Optional("tags"): [str],
            v1.schema.Optional("maintenance_policy"): v1.schema.Or(None, {
                "start_time": str,
                "day": str
            }),
            v1.schema.Optional("auto_upgrade"): bool,
            v1.schema.Optional("surge_upgrade"): bool,
            v1.schema.Optional("ha"): bool
        }
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

        self._cluster_id = self.provider.object_id(f"v2/kubernetes/{self.context.deployment_name}.k8s")

        name = f"{self.context.deployment_name}.k8s"
        name = name.replace(".", "-")

        obj = {
            "kind": "v2/kubernetes",
            "name": f"{self.context.deployment_name}.k8s",
            "params": {
                "name": name,
                "region": self.provider.region(),
                "vpc_uuid": self.provider.vpc_id()
            }
        }

        obj["params"] = v1.utils.merge_dicts(obj["params"], self.configuration)

        for pool in obj["params"]["node_pools"]:
            pool["name"] = f"{name}-{pool['name']}"

        self.provider.add_object(obj)

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""

        client = self.provider.client()

        cluster_id = v1.utils.resolve_futures(self._cluster_id)
        config = dolib.kubeconfig(client, cluster_id)

        return kubernetes.config.load_kube_config_from_dict(config)


repository = {
    "v1": {
        "bonds": {
            "torquetech.io/do": [
                KubernetesClient
            ]
        }
    }
}
