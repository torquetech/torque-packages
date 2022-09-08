# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes

from torque import v1
from torque import k8slib


class KubernetesClientInterface(v1.bond.Bond):
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
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

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

        self._current_state = {}
        self._new_state = {}

    def _load_state(self) -> dict[str, object]:
        """TODO"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", self) or {}

    def _store_state(self):
        """TODO"""

        with self.context as ctx:
            ctx.set_data("state", self, self._current_state)

    def on_apply(self, dry_run: bool):
        """TODO"""

        client = self.bonds.client.connect()
        self._load_state()

        try:
            k8slib.apply(client,
                         self._current_state,
                         self._new_state,
                         self.configuration["quiet"])

        finally:
            self._store_state()

    def on_delete(self, dry_run: bool):
        """TODO"""

        client = self.bonds.client.connect()
        self._load_state()

        try:
            k8slib.apply(client,
                         self._current_state,
                         self._new_state,
                         self.configuration["quiet"])

        finally:
            self._store_state()

    def on_command(self, argv: [str]):
        """TODO"""

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            if "namespace" in obj["metadata"]:
                name = f"{obj['metadata']['namespace']}/"

            name += f"{obj['kind']}/{obj['metadata']['name']}"

            if name in self._new_state:
                raise RuntimeError(f"{name}: k8s object already exists")

            self._new_state[name] = obj

    def namespace(self) -> str:
        """TODO"""

        return self.configuration["namespace"]


repository = {
    "v1": {
        "interfaces": [
            KubernetesClientInterface
        ],
        "providers": {
            "torquetech.io/k8s": Provider
        }
    }
}
