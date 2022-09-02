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

    def load_bucket(self, name: str) -> dict[str, object]:
        """TODO"""

        bucket_path = f"{self._path}/{name}.yaml"

        if not os.path.exists(bucket_path):
            return {}

        with open(bucket_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def store_bucket(self, name: str, data: dict[str, object]):
        """TODO"""

        bucket_path = f"{self._path}/{name}.yaml"

        with open(f"{bucket_path}.tmp", "w", encoding="utf-8") as file:
            yaml.safe_dump(data,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{bucket_path}.tmp", bucket_path)

    def path(self) -> str:
        """TODO"""

        return self._path


class NullProvider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
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

        return {}

    def on_apply(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_delete(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_command(self, context: v1.deployment.Context, argv: [str]):
        """TODO"""
