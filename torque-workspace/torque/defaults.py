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


class LocalContext(v1.deployment.Context):
    """TODO"""

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
