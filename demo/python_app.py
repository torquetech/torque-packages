# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import shutil
import subprocess

from torque import v1

from demo import components
from demo import providers
from demo import types
from demo import utils


def _validate_replicas(replicas: object) -> int:
    """TODO"""

    if replicas is None:
        raise ValueError()

    replicas = int(replicas)

    if replicas < 1 or replicas > 32:
        raise ValueError()

    return replicas


class Component(v1.component.Component):
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
            "replicas": v1.schema.Use(_validate_replicas),
            "environment": {
                v1.schema.Optional(str): str
            }
        }
    }

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._PARAMETERS["schema"],
                                        cls._PARAMETERS["defaults"],
                                        parameters)

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {
            "images": {
                "interface": providers.Images,
                "required": True
            },
            "deployments": {
                "interface": providers.Deployments,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._network_links = []
        self._volume_links = []
        self._secret_links = []
        self._environment = []
        self._ports = []

        self._version = None

    def _path(self) -> str:
        """TODO"""

        return v1.utils.resolve_path(self.parameters["path"])

    def _get_version(self) -> str:
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

    def _image(self, deployment: v1.deployment.Deployment) -> str:
        """TODO"""

        return f"{deployment.name}-component-{self.name}:{self._get_version()}"

    def _add_network_link(self, name: str, link: v1.utils.Future[object]):
        """TODO"""

        link = types.NetworkLink(name, link)
        self._network_links.append(link)

    def _add_volume_link(self, name: str, mount_path: str, link: v1.utils.Future[object]):
        """TODO"""

        link = types.VolumeLink(name, mount_path, link)
        self._volume_links.append(link)

    def _add_secret_link(self, name: str, key: str, link: v1.utils.Future[object]):
        """TODO"""

        link = types.SecretLink(name, key, link)
        self._secret_links.append(link)

    def _add_environment(self, name: str, value: str):
        """TODO"""

        env = types.KeyValue(name, value)
        self._environment.append(env)

    def _get_modules_path(self) -> str:
        """TODO"""

        return f"{self._path()}/modules"

    def _add_requirements(self, requirements: [str]):
        """TODO"""

        requirements += [""]

        with open(f"{self._path()}/requirements.txt", "a", encoding="utf8") as file:
            file.write("\n".join(requirements))

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.NetworkLink(add=self._add_network_link),
            components.VolumeLink(add=self._add_volume_link),
            components.SecretLink(add=self._add_secret_link),
            components.Environment(add=self._add_environment),
            components.PythonModules(path=self._get_modules_path,
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

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

        cmd = [
            "docker", "build", ".",
            "-t", self._image(deployment)
        ]

        subprocess.run(cmd, env=os.environ, cwd=self._path(), check=True)

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        env = [
            types.KeyValue(name, value)
            for name, value in self.configuration["environment"].items()
        ]

        env += self._environment

        self.interfaces.images.push(self._image(deployment))
        self.interfaces.deployments.create(self.name,
                                           self._image(deployment),
                                           None,
                                           None,
                                           None,
                                           env,
                                           self._ports,
                                           self._network_links,
                                           self._volume_links,
                                           self._secret_links,
                                           self.configuration["replicas"])
