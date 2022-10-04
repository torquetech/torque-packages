# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import sys
import time

import kubernetes
import yaml

from torque import v1
from torque import k8s
from torque import do
from torque import dolib


class _V2KubernetesClusters:
    """TODO"""

    @classmethod
    def _create_pool(cls,
                     client: dolib.Client,
                     cluster_id: str,
                     pool_name: str,
                     params: dict[str, object]):
        """TODO"""

        print(f"{pool_name} creating...", file=sys.stdout)

        res = client.post(f"v2/kubernetes/clusters/{cluster_id}/node_pools", params)
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{pool_name}: {data['message']}")

    @classmethod
    def _update_pool(cls,
                     client: dolib.Client,
                     cluster_id: str,
                     pool_id: str,
                     pool_name: str,
                     params: dict[str, object]):
        """TODO"""

        print(f"{pool_name} updating...", file=sys.stdout)

        res = client.put(f"v2/kubernetes/clusters/{cluster_id}/node_pools/{pool_id}", params)
        data = res.json()

        if res.status_code != 202:
            raise v1.exceptions.RuntimeError(f"{pool_name}: {data['message']}")

    @classmethod
    def _delete_pool(cls,
                     client: dolib.Client,
                     cluster_id: str,
                     pool_id: str,
                     pool_name: str):
        """TODO"""

        print(f"{pool_name} deleting...", file=sys.stdout)

        client.delete(f"v2/kubernetes/clusters/{cluster_id}/node_pools/{pool_id}")

    @classmethod
    def _update_pools(cls,
                      client: dolib.Client,
                      old_obj: dict[str, object],
                      new_obj: dict[str, object]):
        """TODO"""

        cluster_id = old_obj["metadata"]["id"]

        current_pools = dict(old_obj["metadata"]["node_pools"].items())
        new_pools = {
            pool["name"]: pool for pool in new_obj["params"]["node_pools"]
        }

        if not new_pools:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: at least one node pool is required")

        for name, new_pool in new_pools.items():
            if name not in current_pools:
                cls._create_pool(client, cluster_id, name, new_pool)

            else:
                pool_id = current_pools[name]

                cls._update_pool(client, cluster_id, pool_id, name, new_pool)

        for name, pool_id in current_pools.items():
            if name in new_pools:
                continue

            cls._delete_pool(client, cluster_id, pool_id, name)

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/kubernetes/clusters", new_obj["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["kubernetes_cluster"]

        attached_pools = {
            pool["name"]: pool["id"] for pool in data["node_pools"]
        }

        return new_obj | {
            "metadata": {
                "id": data["id"],
                "node_pools": {
                    pool["name"]: attached_pools[pool["name"]]
                    for pool in new_obj["params"]["node_pools"]
                }
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        cls._update_pools(client, old_obj, new_obj)

        params = {} | new_obj["params"]

        params.pop("node_pools")
        params.pop("ha", None)

        res = client.put(f"v2/kubernetes/clusters/{old_obj['metadata']['id']}", params)
        data = res.json()

        if res.status_code != 202:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["kubernetes_cluster"]

        attached_pools = {
            pool["name"]: pool["id"] for pool in data["node_pools"]
        }

        return new_obj | {
            "metadata": {
                "id": data["id"],
                "node_pools": {
                    pool["name"]: attached_pools[pool["name"]]
                    for pool in new_obj["params"]["node_pools"]
                }
            }
        }

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/kubernetes/clusters/{old_obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""

        cluster_name = obj["name"]
        cluster_id = obj["metadata"]["id"]

        while True:
            res = client.get(f"v2/kubernetes/clusters/{cluster_id}")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{cluster_name}: {data['message']}")

            data = data["kubernetes_cluster"]
            done = data["status"]["state"] == "running"

            for pool in data["node_pools"]:
                for node in pool["nodes"]:
                    done &= node["status"]["state"] == "running"

            if done:
                break

            print(f"waiting for cluster {cluster_name} to become ready...",
                  file=sys.stdout)

            time.sleep(10)


def _kubeconfig(client: dolib.Client, cluster_id: str) -> dict[str, object]:
    """TODO"""

    res = client.get(f"v2/kubernetes/clusters/{cluster_id}/kubeconfig?"
                     "expiry_seconds=3600")

    if res.status_code != 200:
        raise v1.exceptions.RuntimeError(f"{cluster_id}: unable to get kubeconfig")

    return yaml.safe_load(res.text)


class V1Provider(v1.provider.Provider):
    """TODO"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("ha"): bool
        }
    }

    CONFIGURATION = {
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
            v1.schema.Optional("surge_upgrade"): bool
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._params = None

        self._load_params()
        self._create()

    def _load_params(self):
        """TODO"""

        with self.context as ctx:
            self._params = ctx.get_data("parameters", v1.utils.fqcn(self))

            if not self._params:
                self._params = {
                    "ha": self.parameters.get("ha", False)
                }

                ctx.set_data("parameters", v1.utils.fqcn(self), self._params)

    def _create(self):
        """TODO"""

        name = f"{self.context.deployment_name}.k8s"
        sanitized_name = name.replace(".", "-")

        obj = {
            "kind": "v2/kubernetes",
            "name": name,
            "params": {
                "name": sanitized_name,
                "region": self.interfaces.do.region(),
                "vpc_uuid": self.interfaces.do.vpc_id(),
                "ha": self._params["ha"]
            }
        }

        obj["params"] = v1.utils.merge_dicts(obj["params"], self.configuration)

        for pool in obj["params"]["node_pools"]:
            pool["name"] = f"{sanitized_name}-{pool['name']}"

        self._cluster_id = self.interfaces.do.add_object(obj)

        self.interfaces.do.add_resource("do:kubernetes", self._cluster_id)

    def cluster_id(self) -> v1.utils.Future[str]:
        """TODO"""

        return self._cluster_id


class V1Client(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = k8s.V1ClientInterface

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            },
            "do_k8s": {
                "interface": V1Provider,
                "required": True
            }
        }

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""

        client = self.interfaces.do.client()
        cluster_id = self.interfaces.do_k8s.cluster_id()

        try:
            cluster_id = v1.utils.resolve_futures(cluster_id)

        except v1.exceptions.RuntimeError as e:
            raise k8s.ClusterNotInitialized("digitalocean k8s cluster not initialized") from e

        config = _kubeconfig(client, cluster_id)

        return kubernetes.config.load_kube_config_from_dict(config)


dolib.HANDLERS.update({
    "v2/kubernetes": _V2KubernetesClusters
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1Client
        ]
    }
}
