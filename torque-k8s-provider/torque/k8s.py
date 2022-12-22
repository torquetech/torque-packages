# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import kubernetes

from torque import container_registry
from torque import k8slib
from torque import v1


class ClusterNotInitialized(v1.exceptions.TorqueException):
    """DOCSTRING"""


class V1ClientInterface(v1.bond.Interface):
    """DOCSTRING"""

    def kubeconfig(self) -> dict[str, object]:
        """DOCSTRING"""


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

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
        """DOCSTRING"""

        return {
            "client": {
                "interface": V1ClientInterface,
                "required": True
            },
            "cr": {
                "interface": container_registry.V1Provider,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._kubeconfig = None
        self._client = None

        self._current_state = {}
        self._new_state = {}

        self._namespaces = set()
        self._namespace = self.configuration.get("namespace", self.context.deployment_name)

        self._load_state()

        with self as p:
            p.add_hook("apply-objects", self._apply_namespace)
            p.add_hook("apply-utils", self._apply_container_registry)
            p.add_hook("apply", self._apply)
            p.add_hook("delete", self._delete)

    def _load_state(self):
        """DOCSTRING"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", v1.utils.fqcn(self)) or {}

    def _store_state(self):
        """DOCSTRING"""

        with self.context as ctx:
            ctx.set_data("state", v1.utils.fqcn(self), self._current_state)

    def _connect(self):
        """DOCSTRING"""

        self._kubeconfig = self.interfaces.client.kubeconfig()
        self._client = kubernetes.config.new_client_from_config_dict(self._kubeconfig)

    def _apply_namespace(self):
        """DOCSTRING"""

        if self._namespace == "default":
            return

        self.add_object({
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self._namespace
            }
        })

    def _apply_container_registry(self):
        """DOCSTRING"""

        if not self._namespaces:
            return

        dockerconfig = self.interfaces.cr.login()

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

        self.interfaces.cr.push_images()

    def _update_object(self, name: str):
        """DOCSTRING"""

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
        """DOCSTRING"""

        obj = self._current_state.get(name)

        def _delete_object():
            if not self.configuration["quiet"]:
                print(v1.utils.diff_objects(name, obj, {}))

            k8slib.delete_object(self._client, obj)
            self._current_state.pop(name)

        with self as p:
            p.add_hook("collect-garbage", _delete_object)

    def _apply(self):
        """DOCSTRING"""

        try:
            self._connect()

            v1.utils.apply_objects(self._current_state,
                                   self._new_state,
                                   self._update_object,
                                   self._delete_object)

        finally:
            self._store_state()

    def _delete(self):
        """DOCSTRING"""

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

    def kubeconfig(self) -> dict[str, object]:
        """DOCSTRING"""

        return self._kubeconfig

    def add_object(self, obj: dict[str, object]) -> str:
        """DOCSTRING"""

        with self._lock:
            if "namespace" in obj["metadata"]:
                name = f"{obj['metadata']['namespace']}/"

            else:
                name = ""

            name += f"{obj['kind']}/{obj['metadata']['name']}"

            if name in self._new_state:
                raise v1.exceptions.RuntimeError(f"{name}: k8s object already exists")

            self._new_state[name] = obj

            return name

    def register_image(self, image: str, namespace: str) -> str:
        """DOCSTRING"""

        if not self.interfaces.cr:
            raise v1.exceptions.RuntimeError("container registry not initialized")

        with self._lock:
            self._namespaces.add(namespace)

        return self.interfaces.cr.register_image(image)

    def namespace(self) -> str:
        """DOCSTRING"""

        return self._namespace

    def object(self, name: str) -> dict[str, object]:
        """DOCSTRING"""

        if name not in self._new_state:
            raise v1.exceptions.RuntimeError(f"{name}: object not found")

        return self._new_state[name]

    def objects(self) -> dict[str, object]:
        """DOCSTRING"""

        return self._new_state


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
