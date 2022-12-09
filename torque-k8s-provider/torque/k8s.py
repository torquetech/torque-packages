# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import base64
import json

import kubernetes

from torque import container_registry
from torque import k8slib
from torque import v1


class ClusterNotInitialized(v1.exceptions.TorqueException):
    """TODO"""


class V1ClientInterface(v1.bond.Interface):
    """TODO"""

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""


class V1Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "quiet": True
        },
        "schema": {
            "quiet": bool,
            v1.schema.Optional("namespace"): str,
            v1.schema.Optional("overrides"): dict
        }
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "client": {
                "interface": V1ClientInterface,
                "required": True
            },
            "cr": {
                "interface": container_registry.V1ClientInterface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = None

        self._current_state = {}
        self._new_state = {}

        self._namespaces = set()

        self._namespace = self.configuration.get("namespace", self.context.deployment_name)
        self._namespace = self._namespace.replace(".", "-")
        self._namespace = self._namespace.replace("_", "-")

        self._load_state()

        with self as p:
            p.add_hook("apply", self._apply)
            p.add_hook("delete", self._delete)

        self._setup_namespace()

    def _load_state(self):
        """TODO"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", v1.utils.fqcn(self)) or {}

    def _store_state(self):
        """TODO"""

        with self.context as ctx:
            ctx.set_data("state", v1.utils.fqcn(self), self._current_state)

    def _connect(self):
        """TODO"""

        self._client = self.interfaces.client.connect()

    def _setup_namespace(self):
        """TODO"""

        if self._namespace == "default":
            return

        self.add_object({
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self._namespace
            }
        })

    def _setup_container_registry(self):
        """TODO"""

        auth = self.interfaces.cr.auth()

        server = auth["server"]
        username = auth["username"]
        password = auth["password"]

        auth = f"{username}:{password}"

        auth = auth.encode()
        auth = base64.b64encode(auth)
        auth = auth.decode()

        dockerconfig = json.dumps({
            "auths": {
                server: {
                    "auth": auth
                }
            }
        })

        dockerconfig = dockerconfig.encode()
        dockerconfig = base64.b64encode(dockerconfig)
        dockerconfig = dockerconfig.decode()

        for namespace in self._namespaces:
            self.add_object({
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "registry",
                    "namespace": namespace
                },
                "type": "kubernetes.io/dockerconfigjson",
                "data": {
                    ".dockerconfigjson": dockerconfig
                }
            })

    def _update_object(self, name: str):
        """TODO"""

        overrides = self.configuration.get("overrides", {})
        overrides = overrides.get(name, {})

        old_obj = self._current_state.get(name)

        obj = v1.utils.resolve_futures(self._new_state.get(name))
        obj = v1.utils.merge_dicts(obj, overrides)

        if old_obj == obj:
            return

        if not self.configuration["quiet"]:
            print(v1.utils.diff_objects(name, old_obj, obj))

        k8slib.update_object(self._client, obj)
        self._current_state[name] = obj

    def _delete_object(self, name: str):
        """TODO"""

        obj = self._current_state.get(name)

        def _delete_object():
            if not self.configuration["quiet"]:
                print(v1.utils.diff_objects(name, obj, {}))

            k8slib.delete_object(self._client, obj)
            self._current_state.pop(name)

        with self as p:
            p.add_hook("collect-garbage", _delete_object)

    def _apply(self):
        """TODO"""

        try:
            self._connect()

            if self._namespaces:
                self._setup_container_registry()

            v1.utils.apply_objects(self._current_state,
                                   self._new_state,
                                   self._update_object,
                                   self._delete_object)

        finally:
            self._store_state()

    def _delete(self):
        """TODO"""

        try:
            self._connect()

            v1.utils.apply_objects(self._current_state,
                                   {},
                                   self._update_object,
                                   self._delete_object)

        except ClusterNotInitialized:
            pass

        finally:
            self._store_state()

    def add_object(self, obj: dict[str, object]) -> str:
        """TODO"""

        with self._lock:
            if "namespace" in obj["metadata"]:
                name = f"{obj['metadata']['namespace']}/"

            else:
                name = ""

            name += f"{obj['kind']}/{obj['metadata']['name']}"

            if name in self._new_state:
                raise v1.exceptions.RuntimeError(f"{name}: k8s object already exists")

            self._new_state[name] = obj

    def add_container_registry_to(self, namespace: str):
        """TODO"""

        self._namespaces.add(namespace)

    def namespace(self) -> str:
        """TODO"""

        return self._namespace

    def object(self, name: str) -> dict[str, object]:
        """TODO"""

        if name not in self._new_state:
            raise v1.exceptions.RuntimeError(f"{name}: object not found")

        return self._new_state[name]

    def objects(self) -> dict[str, object]:
        """TODO"""

        return self._new_state


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
