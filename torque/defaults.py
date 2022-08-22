# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os

import yaml

from torque import v1


def _create_path(name: str) -> str:
    """TODO"""

    path = f"{v1.utils.torque_dir()}/local/deployments/{name}"

    if not os.path.exists(path):
        os.makedirs(path)

    return path


class DependencyLink(v1.link.Link):
    """TODO"""

    @classmethod
    def on_parameters(cls, parameters: dict[str, object]) -> dict[str, object]:
        """TODO"""

        return {}

    @classmethod
    def on_configuration(cls, configuration: dict[str, object]) -> dict[str, object]:
        """TODO"""

        return {}

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {}

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, context: v1.deployment.Context):
        """TODO"""

    def on_apply(self, context: v1.deployment.Context):
        """TODO"""


class LocalContext(v1.deployment.Context):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, parameters: dict[str, object]) -> dict[str, object]:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        parameters)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._path = _create_path(self.deployment_name)
        self._state_path = f"{self._path}/state.yaml"

    def load(self):
        """TODO"""

        if not os.path.exists(self._state_path):
            self._objects = {}

        else:
            with open(self._state_path, "r", encoding="utf-8") as file:
                self._objects = yaml.safe_load(file)

    def store(self):
        """TODO"""

        with open(f"{self._state_path}.tmp", "w", encoding="utf-8") as file:
            yaml.safe_dump(self._objects,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self._state_path}.tmp", self._state_path)

    def path(self) -> str:
        """TODO"""

        return self._path
