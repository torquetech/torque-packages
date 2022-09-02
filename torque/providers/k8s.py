# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1
from torque.bonds.interfaces import k8s
from torque.providers import k8slib


def _resolve_futures(obj: object) -> object:
    """TODO"""

    if isinstance(obj, dict):
        return {
            k: _resolve_futures(v) for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            _resolve_futures(v) for v in obj
        ]

    if isinstance(obj, v1.utils.Future):
        return _resolve_futures(obj.get())

    if callable(obj):
        return _resolve_futures(obj())

    return obj


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "quiet": True
        },
        "schema": {
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
                "interface": k8s.KubernetesClient,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._objects = {}

    def _load_objects(self, context: v1.deployment.Context) -> dict[str, object]:
        """TODO"""

        objects = context.get_data("state", self, "objects")

        if not objects:
            return {}

        return objects

    def _store_objects(self,
                       context: v1.deployment.Context,
                       objects: dict[str, object]):
        """TODO"""

        context.set_data("state", self, "objects", objects)

    def on_apply(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

        client = self.bonds.client.connect()
        objects = self._load_objects(context)

        self._objects = _resolve_futures(self._objects)

        try:
            k8slib.apply_objects(client,
                                 objects,
                                 self._objects,
                                 self.configuration["quiet"])

        finally:
            self._store_objects(context, objects)

    def on_delete(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

        client = self.bonds.client.connect()
        objects = self._load_objects(context)

        try:
            k8slib.apply_objects(client,
                                 objects,
                                 {},
                                 self.configuration["quiet"])

        finally:
            self._store_objects(context, objects)

    def on_command(self, context: v1.deployment.Context, argv: [str]):
        """TODO"""

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            if "namespace" in obj["metadata"]:
                name = f"{obj['metadata']['namespace']}/"

            name += f"{obj['metadata']['name']}"

            if name in self._objects:
                raise RuntimeError(f"{name}: k8s object already exists")

            self._objects[name] = obj
