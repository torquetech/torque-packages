# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import codecs
import json

import kubernetes

from torque import container_registry
from torque import k8slib
from torque import v1


class ClusterNotInitialized(v1.exceptions.TorqueException):
    """TODO"""


class ClientInterface(v1.bond.Interface):
    """TODO"""

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "namespace": "default",
            "quiet": True
        },
        "schema": {
            "namespace": str,
            "quiet": bool
        }
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "client": {
                "interface": ClientInterface,
                "required": True
            },
            "cr": {
                "interface": container_registry.ClientInterface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = None

        self._current_state = {}
        self._new_state = {}

        self._namespaces = set()

        self._load_state()

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

    def _load_state(self) -> dict[str, object]:
        """TODO"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", v1.utils.fqcn(self)) or {}

    def _store_state(self):
        """TODO"""

        with self.context as ctx:
            ctx.set_data("state",
                         v1.utils.fqcn(self),
                         self._current_state)

    def _connect(self):
        """TODO"""

        self._client = self.interfaces.client.connect()

    def _setup_container_registry(self):
        """TODO"""

        auth = self.interfaces.cr.auth()

        server = auth["server"]
        username = auth["username"]
        password = auth["password"]

        auth = f"{username}:{password}"
        auth = bytes(auth, encoding="utf-8")
        auth = codecs.encode(auth, encoding="base64")
        auth = str(auth, encoding="utf-8")
        auth = auth.replace("\n", "")

        dockerconfig = json.dumps({
            "auths": {
                server: {
                    "auth": auth
                }
            }
        })

        dockerconfig = bytes(dockerconfig, encoding="utf-8")
        dockerconfig = codecs.encode(dockerconfig, encoding="base64")
        dockerconfig = str(dockerconfig, encoding="utf-8")
        dockerconfig = dockerconfig.replace("\n", "")

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

    def _apply(self):
        """TODO"""

        try:
            self._connect()

            self._setup_container_registry()

            k8slib.apply(self._client,
                         self._current_state,
                         self._new_state,
                         self.configuration["quiet"])

        finally:
            self._store_state()

    def _delete(self):
        """TODO"""

        try:
            self._connect()

            k8slib.apply(self._client,
                         self._current_state,
                         {},
                         self.configuration["quiet"])

        except ClusterNotInitialized:
            pass

        finally:
            self._store_state()

        with self.context as ctx:
            ctx.set_data("parameters", v1.utils.fqcn(self), {})

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            if "namespace" in obj["metadata"]:
                namespace = obj["metadata"]["namespace"]
                self._namespaces.add(namespace)

                name = f"{namespace}/"

            name += f"{obj['kind']}/{obj['metadata']['name']}"

            if name in self._new_state:
                raise v1.exceptions.RuntimeError(f"{name}: k8s object already exists")

            self._new_state[name] = obj

    def namespace(self) -> str:
        """TODO"""

        return self.configuration["namespace"]


repository = {
    "v1": {
        "providers": [
            Provider
        ]
    }
}
