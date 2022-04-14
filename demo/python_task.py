# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import shutil
import subprocess

import schema

from torque import v1

from demo import interfaces
from demo import utils


_DEFAULT_PARAMETERS = {
}

_PARAMETERS_SCHEMA = schema.Schema({
    "path": str
})

_DEFAULT_CONFIGURATION = {
    "replicas": 1,
    "environment": {}
}

_CONFIGURATION_SCHEMA = schema.Schema({
    "replicas": int,
    "environment": {
        schema.Optional(str): str
    }
})


class PythonTask(v1.component.Component):
    """TODO"""

    @staticmethod
    def validate_parameters(parameters: object) -> object:
        """TODO"""

        return utils.validate_schema("parameters",
                                     parameters,
                                     _DEFAULT_PARAMETERS,
                                     _PARAMETERS_SCHEMA)

    @staticmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

        return utils.validate_schema("configuration",
                                     configuration,
                                     _DEFAULT_CONFIGURATION,
                                     _CONFIGURATION_SCHEMA)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._network_links = []
        self._volume_links = []
        self._version = None

    def _path(self) -> str:
        """TODO"""

        return v1.utils.resolve_path(self.parameters["path"])

    def _get_version(self):
        if self._version:
            return self._version

        p = subprocess.run(["./version.sh"],
                           cwd=self._path(),
                           env=os.environ,
                           shell=True,
                           check=True,
                           capture_output=True)

        self._version = p.stdout.decode("utf8").strip()
        return self._version

    def _image(self, deployment: str) -> str:
        """TODO"""

        return f"{deployment}-component-{self.name}:{self._get_version()}"

    def _add_network_link(self, link: v1.interface.Future):
        """TODO"""

        self._network_links.append(link)

    def _add_volume_link(self, mount_point: str, link: v1.interface.Future):
        """TODO"""

        self._volume_links.append((mount_point, link))

    def _get_modules_path(self) -> str:
        """TODO"""

        return f"{self._path()}/modules"

    def _add_requirements(self, requirements: [str]):
        """TODO"""

        requirements += []

        with open(f"{self._path()}/requirements.txt", "a", encoding="utf8") as file:
            file.write("\n".join(requirements))

    def inbound_interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return [
            interfaces.NetworkLink(add=self._add_network_link),
            interfaces.VolumeLink(add=self._add_volume_link),
            interfaces.PythonModules(path=self._get_modules_path,
                                     add_requirements=self._add_requirements)
        ]

    def outbound_interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return []

    def on_create(self):
        """TODO"""

        source_path = f"{utils.module_path()}/templates/task"
        target_path = self._path()

        if os.path.exists(target_path):
            raise RuntimeError(f"{target_path}: path already exists")

        shutil.copytree(source_path, target_path)

    def on_remove(self):
        """TODO"""

    def on_build(self, build: v1.build.Build) -> bool:
        """TODO"""

        cmd = [
            "docker", "build", ".",
            "-t", self._image(build.deployment)
        ]

        subprocess.run(cmd, env=os.environ, cwd=self._path(), check=True)

        return True

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        with deployment.interface(interfaces.SimpleDeployment, self.labels) as iface:
            iface.push_image(self._image(deployment.name))
            iface.create_task(self.name,
                              self._image(deployment.name),
                              None,
                              None,
                              self.configuration["environment"],
                              self._network_links,
                              self._volume_links,
                              self.configuration["replicas"])

        return True
