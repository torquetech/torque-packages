# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os
import subprocess
import threading
import yaml

from torque import v1


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("overrides"): dict
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._objects = {
            "version": "3.9",
            "name": self.context.deployment_name,
            "networks": {
                "default": {
                    "name": self.context.deployment_name
                }
            },
            "services": {},
            "volumes": {},
            "configs": {}
        }

        self._lock = threading.Lock()

        with self as p:
            p.add_hook("apply", self._apply)
            p.add_hook("delete", self._delete)

    def _apply(self):
        """DOCSTRING"""

        compose = f"{self.context.path()}/docker-compose.yaml"

        objects = v1.utils.resolve_futures(self._objects)
        objects = v1.utils.merge_dicts(objects, self.configuration.get("overrides", {}))

        with open(compose, "w", encoding="utf8") as file:
            yaml.safe_dump(objects,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        cmd = [
            "docker", "compose",
            "up", "-d",
            "--remove-orphans"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=True)

    def _delete(self):
        """DOCSTRING"""

        cmd = [
            "docker", "compose",
            "down",
            "--volumes"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=False)

    def add_object(self, section: str, name: str, obj: dict[str, object]):
        """DOCSTRING"""

        with self._lock:
            if section not in self._objects:
                self._objects[section] = {}

            self._objects[section][name] = obj

            return (section, name)

    def object(self, section: str, name: str) -> dict[str, object]:
        """DOCSTRING"""

        if section not in self._objects:
            raise v1.exceptions.RuntimeError(f"{section}: section not found")

        if name not in self._objects[section]:
            raise v1.exceptions.RuntimeError(f"{name}: object not found")

        return self._objects[section][name]

    def objects(self) -> dict[str, object]:
        """DOCSTRING"""

        return self._objects


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
