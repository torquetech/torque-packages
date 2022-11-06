# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import threading
import yaml

from torque import v1


class V1Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._objects = {
            "version": "3.9",
            "services": {},
            "volumes": {},
            "configs": {}
        }

        self._lock = threading.Lock()

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

    def _apply(self):
        """TODO"""

        compose = f"{self.context.path()}/docker-compose.yaml"
        objects = v1.utils.resolve_futures(self._objects)

        with open(compose, "w", encoding="utf8") as file:
            file.write(yaml.safe_dump(objects, sort_keys=False))

        cmd = [
            "docker", "compose",
            "up", "-d",
            "--remove-orphans"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=True)

    def _delete(self):
        """TODO"""

        cmd = [
            "docker", "compose",
            "down",
            "--volumes"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=False)

    def add_object(self, section: str, name: str, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            if section not in self._objects:
                self._objects[section] = {}

            self._objects[section][name] = obj


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
