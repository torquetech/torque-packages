# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes

from torque import v1
from torque import k8slib


class KubernetesClientInterface(v1.bond.Interface):
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
                "interface": KubernetesClientInterface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = None

        self._current_state = {}
        self._new_state = {}

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

    def _apply(self):
        """TODO"""

        self._connect()

        try:
            k8slib.apply(self._client,
                         self._current_state,
                         self._new_state,
                         self.configuration["quiet"])

        finally:
            self._store_state()

    def _delete(self):
        """TODO"""

        self._connect()

        try:
            k8slib.apply(self._client,
                         self._current_state,
                         {},
                         self.configuration["quiet"])

        finally:
            self._store_state()

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            if "namespace" in obj["metadata"]:
                name = f"{obj['metadata']['namespace']}/"

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
