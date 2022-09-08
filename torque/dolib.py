# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import difflib
import functools
import re
import sys
import time
import typing

import requests
import yaml

from torque import v1


class Client:
    """TODO"""

    def __init__(self, endpoint: str, token: str):
        self._endpoint = endpoint
        self._session = requests.Session()

        self._headers = {
            "Authorization": f"Bearer {token}"
        }

    def post(self, path: str, params: object) -> object:
        """TODO"""

        return self._session.post(f"{self._endpoint}/{path}",
                                  headers=self._headers,
                                  json=params)


    def put(self, path: str, params: object) -> object:
        """TODO"""

        return self._session.put(f"{self._endpoint}/{path}",
                                 headers=self._headers,
                                 json=params)

    def get(self, path: str, params=None) -> object:
        """TODO"""

        return self._session.get(f"{self._endpoint}/{path}",
                                 headers=self._headers,
                                 params=params)

    def delete(self, path: str) -> object:
        """TODO"""

        return self._session.delete(f"{self._endpoint}/{path}",
                                    headers=self._headers)


class V2KubernetesClusters:
    """TODO"""

    @classmethod
    def _create_pool(cls, client: Client, cluster_id: str, pool_name: str, params: dict[str, object]):
        """TODO"""

        print(f"{pool_name} creating...")

        res = client.post(f"v2/kubernetes/clusters/{cluster_id}/node_pools", params)
        data = res.json()

        if res.status_code != 201:
            raise RuntimeError(f"{pool_name}: {data['message']}")

    @classmethod
    def _update_pool(cls,
                    client: Client,
                    cluster_id: str,
                    pool_id: str,
                    pool_name: str,
                    params: dict[str, object]):
        """TODO"""

        print(f"{pool_name} updating...")

        res = client.put(f"v2/kubernetes/clusters/{cluster_id}/node_pools/{pool_id}", params)
        data = res.json()

        if res.status_code != 202:
            raise RuntimeError(f"{pool_name}: {data['message']}")

    @classmethod
    def _delete_pool(cls,
                    client: Client,
                    cluster_id: str,
                    pool_id: str,
                    pool_name: str):
        """TODO"""

        print(f"{pool_name} deleting...")

        res = client.delete(f"v2/kubernetes/clusters/{cluster_id}/node_pools/{pool_id}")

    @classmethod
    def _update_pools(cls,
                      client: Client,
                      old_obj: dict[str, object],
                      new_obj: dict[str, object]):
        """TODO"""

        cluster_id = old_obj["metadata"]["id"]

        current_pools = {
            name: id for name, id in old_obj["metadata"]["node_pools"].items()
        }

        new_pools = {
            pool["name"]: pool for pool in new_obj["params"]["node_pools"]
        }

        if not new_pools:
            raise RuntimeError(f"{new_obj['name']}: at least one node pool is required")

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
    def create(cls, client: Client, obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/kubernetes/clusters", obj["params"])
        data = res.json()

        if res.status_code != 201:
            raise RuntimeError(f"{obj['name']}: {data['message']}")

        data = data["kubernetes_cluster"]

        attached_pools = {
            pool["name"]: pool["id"] for pool in data["node_pools"]
        }

        return {
            "kind": obj["kind"],
            "name": obj["name"],
            "metadata": {
                "id": data["id"],
                "node_pools": {
                    pool["name"]: attached_pools[pool["name"]]
                    for pool in obj["params"]["node_pools"]
                }
            },
            "params": obj["params"]
        }

    @classmethod
    def update(cls,
               client: Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        cls._update_pools(client, old_obj, new_obj)

        params = {} | new_obj["params"]

        params.pop("node_pools")
        params.pop("ha")

        res = client.put(f"v2/kubernetes/clusters/{old_obj['metadata']['id']}", params)
        data = res.json()

        if res.status_code != 202:
            raise RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["kubernetes_cluster"]

        attached_pools = {
            pool["name"]: pool["id"] for pool in data["node_pools"]
        }

        return {
            "kind": new_obj["kind"],
            "name": new_obj["name"],
            "metadata": {
                "id": data["id"],
                "node_pools": {
                    pool["name"]: attached_pools[pool["name"]]
                    for pool in new_obj["params"]["node_pools"]
                }
            },
            "params": new_obj["params"]
        }

    @classmethod
    def delete(cls, client: Client, obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/kubernetes/clusters/{obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: Client, obj: dict[str, object]):
        """TODO"""

        cluster_name = obj["name"]
        cluster_id = obj["metadata"]["id"]

        while True:
            res = client.get(f"v2/kubernetes/clusters/{cluster_id}")
            data = res.json()

            if res.status_code != 200:
                raise RuntimeError(f"{cluster_name}: {data['message']}")

            data = data["kubernetes_cluster"]
            done = data["status"]["state"] == "running"

            for pool in data["node_pools"]:
                for node in pool["nodes"]:
                    done &= node["status"]["state"] == "running"

            if done:
                break

            print(f"waiting for cluster {cluster_name} to become ready...")

            time.sleep(10)


class V2Certificates:
    """TODO"""

    @classmethod
    def create(cls, client: Client, obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/certificates", obj["params"])
        data = res.json()

        if res.status_code != 201:
            raise RuntimeError(f"{obj['name']}: {data['message']}")

        return {
            "kind": obj["kind"],
            "name": obj["name"],
            "metadata": {
                "id": data["certificate"]["id"]
            },
            "params": obj["params"]
        }

    @classmethod
    def update(cls,
               client: Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise RuntimeError(f"{old_obj['name']}: cannot update certificates")

    @classmethod
    def delete(cls, client: Client, obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/certificates/{obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: Client, obj: dict[str, object]):
        """TODO"""


HANDLERS = {
    "v2/kubernetes": V2KubernetesClusters,
    "v2/certificates": V2Certificates
}


def connect(endpoint: str, token: str) -> Client:
    """TODO"""

    return Client(endpoint, token)


def setup_project(client: Client, name: str) -> dict[str, object]:
    """TODO"""

    res = client.get("v2/projects")
    data = res.json()

    if res.status_code != 200:
        raise RuntimeError(f"setup_project(): {data['message']}")

    for project in data["projects"]:
        if name == project["name"]:
            return project

    params = {
        "name": name,
        "purpose": "torquetech.io deployment",
        "environment": "Production"
    }

    res = client.post("v2/projects", params)
    data = res.json()

    if res.status_code != 201:
        raise RuntimeError(f"{name}: {data['message']}")

    return data["project"]


def setup_vpc(client: Client, name: str, region: str) -> dict[str, object]:
    """TODO"""

    page = 0

    while True:
        page += 1

        params = {
            "per_page": 20,
            "page": page
        }

        res = client.get("v2/vpcs", params)
        data = res.json()

        if res.status_code != 200:
            raise RuntimeError(f"setup_project(): {data['message']}")

        for vpc in data["vpcs"]:
            if name == vpc["name"]:
                return vpc

        if len(data["vpcs"]) != 20:
            break

    params = {
        "name": name,
        "region": region
    }

    res = client.post("v2/vpcs", params)
    data = res.json()

    if res.status_code != 201:
        raise RuntimeError(f"{name}: {data['message']}")

    return data["vpc"]


def kubeconfig(client: Client, cluster_id: str) -> dict[str, object]:
    """TODO"""

    res = client.get(f"v2/kubernetes/clusters/{cluster_id}/kubeconfig")

    if res.status_code != 200:
        raise RuntimeError(f"{cluster_id}: unable to get kubeconfig")

    return yaml.safe_load(res.text)


def _diff(name: str, obj1: dict[str, object], obj2: dict[str, object]):
    """TODO"""

    obj1 = yaml.safe_dump(obj1, sort_keys=False) if obj1 else ""
    obj2 = yaml.safe_dump(obj2, sort_keys=False) if obj2 else ""

    diff = difflib.unified_diff(obj1.split("\n"),
                                obj2.split("\n"),
                                fromfile=f"a/{name}",
                                tofile=f"b/{name}",
                                lineterm="")

    diff = "\n".join(diff)

    return obj1 != obj2, diff


def apply(client: Client,
          current_state: dict[str, object],
          new_state: dict[str, object],
          quiet: bool) -> [typing.Callable]:
    """TODO"""

    wait_hooks = []

    for name, new_obj in new_state.items():
        current_obj = current_state.get(name, None)
        new_obj = v1.utils.resolve_futures(new_obj)

        current_params = None
        new_params = new_obj["params"]

        if current_obj:
            current_params = current_obj["params"]

        changed, diff = _diff(name, current_params, new_params)

        if not changed:
            continue

        if not quiet:
            if not current_obj:
                print(f"creating {name}...", file=sys.stdout)

            else:
                print(f"updating {name}...", file=sys.stdout)

        if not quiet:
            print(diff, file=sys.stdout)

        handler = HANDLERS[new_obj["kind"]]

        if not current_obj:
            new_obj = handler.create(client, new_obj)

        else:
            new_obj = handler.update(client, current_obj, new_obj)

        current_state[name] = new_obj

        wait_hooks.append(functools.partial(handler.wait, client, new_obj))

    for name, current_obj in list(current_state.items()):
        if name in new_state:
            continue

        if not quiet:
            print(f"deleting {name}...", file=sys.stdout)

        _, diff = _diff(name, current_obj["params"], None)

        if not quiet:
            print(diff, file=sys.stdout)

        handler = HANDLERS[current_obj["kind"]]
        handler.delete(client, current_obj)

        current_state.pop(name)

    return wait_hooks
