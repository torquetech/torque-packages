# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes
import yaml

from torque import do
from torque import dolib
from torque import k8s
from torque import v1


class _V2KubernetesClusters(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_params = None
        self._cluster_name = self._object["cluster_name"]

        self._current_pools = None
        self._current_pool_map = None

        self._cluster_id = None
        self._pools = None

        if "metadata" in self._object:
            self._cluster_id = self._object["metadata"]["id"]

    def _update_pool(self, name: str):
        """TODO"""

        if name not in self._current_pools:
            res = self._client.post(f"v2/kubernetes/clusters/{self._cluster_id}/"
                                    "node_pools", self._pools[name])
            data = res.json()

            if res.status_code != 201:
                raise v1.exceptions.RuntimeError(f"{self._name}: {name}: {data['message']}")

            return

        current_params = self._current_pools[name]

        params = {} | self._pools[name]
        tags = params["tags"]

        builtin_tags = [
            "k8s",
            "k8s:worker",
            f"k8s:{self._cluster_id}"
        ]

        for tag in builtin_tags:
            if tag not in tags and tag in current_params["tags"]:
                current_params["tags"].remove(tag)

        if current_params == params:
            return

        pool_id = self._current_pool_map[name]

        res = self._client.put(f"v2/kubernetes/clusters/{self._cluster_id}/"
                               f"node_pools/{pool_id}", self._pools[name])
        data = res.json()

        if res.status_code != 202:
            raise v1.exceptions.RuntimeError(f"{self._name}: {name}: {data['message']}")

    def _delete_pool(self, name: str):
        """TODO"""

        pool_id = self._current_pool_map[name]

        res = self._client.delete(f"v2/kubernetes/clusters/{self._cluster_id}/node_pools/{pool_id}")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")

    def _update_pools(self):
        """TODO"""

        self._pools = {
            pool["name"]: pool for pool in self._object["params"]["node_pools"]
        }

        v1.utils.apply_objects(self._current_pools,
                               self._pools,
                               self._update_pool,
                               self._delete_pool)

    def _get(self) -> bool:
        """TODO"""

        page = 1

        while True:
            res = self._client.get(f"v2/kubernetes/clusters?page={page}&per_page=20")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

            clusters = data["kubernetes_clusters"]

            for cluster in clusters:
                if self._cluster_name == cluster["name"]:
                    self._current_params = {
                        "name": cluster["name"],
                        "region": cluster["region"],
                        "vpc_uuid": cluster["vpc_uuid"],
                        "ha": cluster["ha"],
                        "tags": cluster["tags"],
                        "maintenance_policy": cluster["maintenance_policy"],
                        "auto_upgrade": cluster["auto_upgrade"],
                        "surge_upgrade": cluster["surge_upgrade"],
                        "node_pools": [{
                            "size": pool["size"],
                            "name": pool["name"],
                            "count": pool["count"],
                            "tags": pool["tags"],
                            "labels": pool["labels"] or {},
                            "taints": pool["taints"],
                            "auto_scale": pool["auto_scale"],
                            "min_nodes": pool["min_nodes"],
                            "max_nodes": pool["max_nodes"]
                        } for pool in cluster["node_pools"]]
                    }

                    self._current_pools = {
                        pool["name"]: pool for pool in self._current_params["node_pools"]
                    }

                    self._current_pool_map = {
                        pool["name"]: pool["id"] for pool in cluster["node_pools"]
                    }

                    self._cluster_id = cluster["id"]

                    return True

            if len(clusters) != 20:
                break

            page += 1

        return False

    def _create(self):
        """TODO"""

        res = self._client.post("v2/kubernetes/clusters", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._cluster_id = data["kubernetes_cluster"]["id"]

    def _check_immutable_params(self):
        """TODO"""

        if self._current_params["ha"] != self._object["params"]["ha"]:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify ha parameter")

        if self._current_params["vpc_uuid"] != self._object["params"]["vpc_uuid"]:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify vpc_uuid parameter")

        if self._current_params["region"] != self._object["params"]["region"]:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify region parameter")

    def _update_cluster(self):
        """TODO"""

        current_maintenance_policy = {} | self._current_params["maintenance_policy"]
        current_maintenance_policy.pop("duration")

        current_params = self._current_params
        current_params = {
            "tags": sorted(current_params["tags"]),
            "maintenance_policy": current_maintenance_policy,
            "auto_upgrade": current_params["auto_upgrade"],
            "surge_upgrade": current_params["surge_upgrade"]
        }

        params = self._object["params"]
        tags = params.get("tags", [])

        builtin_tags = [
            "k8s",
            f"k8s:{self._cluster_id}"
        ]

        for tag in builtin_tags:
            if tag not in tags and tag in current_params["tags"]:
                current_params["tags"].remove(tag)

        params = {
            "tags": sorted(tags),
            "maintenance_policy": params["maintenance_policy"],
            "auto_upgrade": params["auto_upgrade"],
            "surge_upgrade": params["surge_upgrade"]
        }

        if current_params == params:
            return

        res = self._client.put(f"v2/kubernetes/clusters/{self._cluster_id}", params)
        data = res.json()

        if res.status_code != 202:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update(self):
        """TODO"""

        self._check_immutable_params()

        self._update_cluster()
        self._update_pools()

    def _wait(self):
        """TODO"""

        def cond():
            res = self._client.get(f"v2/kubernetes/clusters/{self._cluster_id}")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

            data = data["kubernetes_cluster"]
            done = data["status"]["state"] == "running"

            for pool in data["node_pools"]:
                for node in pool["nodes"]:
                    done &= node["status"]["state"] == "running"

            return done

        v1.utils.wait_for(cond, f"waiting for cluster {self._name} to become ready")

    def update(self) -> dict[str, object]:
        """TODO"""

        if not self._get():
            self._create()

        else:
            self._update()

        self._wait()

        return self._object | {
            "metadata": {
                "id": self._cluster_id
            }
        }

    def delete(self):
        """TODO"""

        with self._context as ctx:
            ctx.delete_secret_data(self._object["name"], "kubeconfig")

        res = self._client.delete(f"v2/kubernetes/clusters/{self._cluster_id}"
                                  "/destroy_with_associated_resources/dangerous")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


def _kubeconfig(client: dolib.Client, cluster_id: str) -> dict[str, object]:
    """TODO"""

    res = client.get(f"v2/kubernetes/clusters/{cluster_id}/kubeconfig?expiry_seconds=315360000")

    if res.status_code != 200:
        raise v1.exceptions.RuntimeError(f"{cluster_id}: unable to get kubeconfig")

    return yaml.safe_load(res.text)


class V1Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "ha": False,
            "node_pools": [{
                "size": "s-1vcpu-2gb",
                "name": "pool-1",
                "count": 2,
                "tags": [],
                "labels": {},
                "taints": [],
                "auto_scale": False,
                "min_nodes": 1,
                "max_nodes": 1
            }],
            "tags": [],
            "maintenance_policy": {
                "start_time": "10:00",
                "day": "any"
            },
            "auto_upgrade": False,
            "surge_upgrade": False
        },
        "schema": {
            "ha": bool,
            "node_pools": [{
                "size": str,
                "name": str,
                "count": int,
                "tags": [str],
                "labels": {
                    v1.schema.Optional(str): str
                },
                "taints": [{
                    "key": str,
                    "value": str,
                    "effect": v1.schema.Or("NoSchedule",
                                           "PreferNoSchedule",
                                           "NoExecute")
                }],
                "auto_scale": bool,
                "min_nodes": int,
                "max_nodes": int
            }],
            "tags": [str],
            "maintenance_policy": {
                "start_time": str,
                "day": str
            },
            "auto_upgrade": bool,
            "surge_upgrade": bool
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

        self._cluster_name = f"{self.context.deployment_name}.k8s"
        self._cluster_id = None

        self._create_cluster()

    def _create_cluster(self):
        """TODO"""

        sanitized_name = self._cluster_name.replace(".", "-")

        obj = {
            "kind": "v2/kubernetes",
            "name": self._cluster_name,
            "cluster_name": sanitized_name,
            "params": {
                "name": sanitized_name,
                "region": self.interfaces.do.region(),
                "vpc_uuid": self.interfaces.do.vpc_id(),
                "version": "latest"
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

    def cluster_name(self) -> str:
        """TODO"""

        return self._cluster_name


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

        with self.context as ctx:
            config = ctx.get_secret_data(self.interfaces.do_k8s.cluster_name(), "kubeconfig")

            if not config:
                cluster_id = self.interfaces.do_k8s.cluster_id()

                try:
                    cluster_id = v1.utils.resolve_futures(cluster_id)

                except v1.exceptions.RuntimeError as e:
                    raise k8s.ClusterNotInitialized("digitalocean k8s cluster not initialized") from e

                client = self.interfaces.do.client()
                config = _kubeconfig(client, cluster_id)

                ctx.set_secret_data(self.interfaces.do_k8s.cluster_name(), "kubeconfig", config)

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
