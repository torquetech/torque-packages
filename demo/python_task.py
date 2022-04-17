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


class Task(v1.component.Component):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {
            "path": str
        }
    }

    _CONFIGURATION = {
        "defaults": {
            "replicas": 1,
            "environment": {}
        },
        "schema": {
            "replicas": int,
            "environment": {
                schema.Optional(str): str
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._network_links = []
        self._volume_links = []
        self._secrets = []
        self._environment = []
        self._version = None

    @classmethod
    def validate_parameters(cls, parameters: object) -> object:
        """TODO"""

        return utils.validate_schema("parameters",
                                     cls._PARAMETERS,
                                     parameters)

    @classmethod
    def validate_configuration(cls, configuration: object) -> object:
        """TODO"""

        return utils.validate_schema("configuration",
                                     cls._CONFIGURATION,
                                     configuration)

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

    def _add_secret(self,
                    name: str,
                    obj: object,
                    key: str):
        """TODO"""

        self._secrets.append(interfaces.Provider.Secret(name, obj, key))

    def _add_environment(self, name: str, value: str):
        """TODO"""

        self._environment.append(interfaces.Provider.KeyValue(name, value))

    def _get_modules_path(self) -> str:
        """TODO"""

        return f"{self._path()}/modules"

    def _add_requirements(self, requirements: [str]):
        """TODO"""

        requirements += [""]

        with open(f"{self._path()}/requirements.txt", "a", encoding="utf8") as file:
            file.write("\n".join(requirements))

    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return [
            interfaces.NetworkLink(add=self._add_network_link),
            interfaces.VolumeLink(add=self._add_volume_link),
            interfaces.Secret(add=self._add_secret),
            interfaces.Environment(add=self._add_environment),
            interfaces.PythonModules(path=self._get_modules_path,
                                     add_requirements=self._add_requirements)
        ]

    def on_create(self):
        """TODO"""

        source_path = f"{utils.module_path()}/templates/python_app"
        target_path = self._path()

        if os.path.exists(target_path):
            raise RuntimeError(f"{target_path}: path already exists")

        shutil.copytree(source_path, target_path)

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        cmd = [
            "docker", "build", ".",
            "-t", self._image(deployment.name)
        ]

        subprocess.run(cmd, env=os.environ, cwd=self._path(), check=True)

        return True

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        env = [
            interfaces.Provider.KeyValue(name, value)
            for name, value in self.configuration["environment"].items()
        ]

        env += self._environment

        provider = deployment.interface(interfaces.Provider)

        provider.push_image(self._image(deployment.name))
        provider.create_deployment(self.name,
                                   self._image(deployment.name),
                                   None,
                                   None,
                                   None,
                                   env,
                                   self._network_links,
                                   self._volume_links,
                                   self._secrets,
                                   self.configuration["replicas"])

        return True
