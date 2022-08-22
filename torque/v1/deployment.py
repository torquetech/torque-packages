# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import secrets
import threading

from . import utils


class Context:
    # pylint: disable=R0902

    """TODO"""

    def __init__(self, deployment_name: str, configuration: dict[str, object]):
        # pylint: disable=R0913

        self.deployment_name = deployment_name
        self.configuration = configuration
        self.dry_run = False

        self._objects: dict[str, object] = None
        self._objects_lock = threading.Lock()

    def _get_object(self, type: str, name: str) -> bytes:
        """TODO"""

        name = f"{type}-{name}"

        # pylint: disable=E1135
        if name not in self._objects:
            return {}

        # pylint: disable=E1136
        return self._objects[name]

    def _set_object(self, type: str, name: str, data: bytes):
        """TODO"""

        name = f"{type}-{name}"

        # pylint: disable=E1137
        self._objects[name] = data

    def get_object(self, type: str, name: str) -> bytes:
        """TODO"""

        with self._objects_lock:
            return self._get_object(type, name)

    def set_object(self, type: str, name: str, data: bytes):
        """TODO"""

        with self._objects_lock:
            self._set_object(type, name, data)

    def secret(self, name: str, length: int = 16) -> str:
        """TODO"""

        with self._objects_lock:
            s = self._get_object("secret", name)

            if not s:
                s = secrets.token_urlsafe(length)
                self._set_object("secret", name, s.encode("utf-8"))

            else:
                s = s.decode("utf-8")

            return s

    @classmethod
    def on_configuration(cls, parameters: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    def load(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: load: not implemented")

    def store(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: store: not implemented")

    def path(self) -> str:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: path: not implemented")
