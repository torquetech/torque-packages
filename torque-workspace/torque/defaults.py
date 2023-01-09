# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os

import yaml

from torque import v1


def _create_path(context_path: str) -> str:
    """DOCSTRING"""

    path = f"{v1.utils.torque_dir()}/{context_path}"

    if not os.path.exists(path):
        os.makedirs(path)

    return path


class V1DependencyLink(v1.link.Link):
    """DOCSTRING"""


class V1LocalContext(v1.deployment.Context):
    """DOCSTRING"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("workspace_path"): str
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context_path = f"local/deployments/{self.deployment_name}"
        self._path = _create_path(context_path)

        workspace_path = self.configuration.get("workspace_path")

        if workspace_path:
            self._external_path = f"{workspace_path}/.torque/{context_path}"

        else:
            self._external_path = self._path

    def load_bucket(self, name: str) -> dict[str, object]:
        """DOCSTRING"""

        bucket_path = f"{self._path}/{name}.yaml"

        if not os.path.exists(bucket_path):
            return {}

        with open(bucket_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def store_bucket(self, name: str, data: dict[str, object]):
        """DOCSTRING"""

        bucket_path = f"{self._path}/{name}.yaml"

        with open(f"{bucket_path}.tmp", "w", encoding="utf-8") as file:
            yaml.safe_dump(data,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{bucket_path}.tmp", bucket_path)

    def path(self) -> str:
        """DOCSTRING"""

        return self._path

    def external_path(self) -> str:
        """DOCSTRING"""

        return self._external_path


repository = {
    "v1": {
        "contexts": [
            V1LocalContext
        ],
        "links": [
            V1DependencyLink
        ]
    }
}
