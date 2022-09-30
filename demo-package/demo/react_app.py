# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import json
import os
import shutil
import subprocess

from torque import v1

from demo import components
from demo import providers
from demo import types
from demo import utils


class Component(v1.component.Component):
    """TODO"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            "path": str
        }
    }

    CONFIGURATION = {
        "defaults": {
            "development_mode": False
        },
        "schema": {
            "development_mode": bool
        }
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "images": {
                "interface": providers.Images,
                "required": True
            },
            "deployments": {
                "interface": providers.Deployments,
                "required": True
            },
            "services": {
                "interface": providers.Services,
                "required": True
            },
            "development": {
                "interface": providers.Development,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._service_link = None
        self._version = None

    def _path(self) -> str:
        """TODO"""

        return v1.utils.resolve_path(self.parameters["path"])

    def _load_package(self) -> dict:
        """TODO"""

        package_path = f"{self._path()}/package.json"

        with open(package_path, encoding="utf8") as file:
            return json.load(file)

    def _get_version(self) -> str:
        if self._version:
            return self._version

        package = self._load_package()

        self._version = package["version"]
        return self._version

    def _image(self) -> str:
        """TODO"""

        return f"{self.context.deployment_name}-component-{self.name}:{self._get_version()}"

    def _link(self) -> utils.Future[object]:
        """TODO"""

        return self._service_link

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.HttpService(link=self._link)
        ]

    def on_create(self):
        """TODO"""

        source_path = f"{utils.module_path()}/templates/react_app"
        target_path = self._path()

        if os.path.exists(target_path):
            raise RuntimeError(f"{target_path}: path already exists")

        shutil.copytree(source_path, target_path)

    def on_build(self):
        """TODO"""

        cmd = [
            "docker", "build", ".",
            "-t", self._image()
        ]

        if self.configuration["development_mode"]:
            cmd += ["-f", "Dockerfile.dev"]

        subprocess.run(cmd, env=os.environ, cwd=self._path(), check=True)

    def on_apply(self):
        """TODO"""

        self._service_link = self.interfaces.services.create(self.name, "tcp", 80, 80)

        image = self.interfaces.images.push(self._image())

        if not self.configuration["development_mode"]:
            self.interfaces.deployments.create(self.name,
                                               image,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None)

        else:
            if not self.interfaces.development:
                raise RuntimeError("providers.Development: implementation not found")

            local_volume_links = [
                types.VolumeLink("app", "/app", utils.Future(self.parameters["path"]))
            ]

            self.interfaces.development.create_deployment(self.name,
                                                     image,
                                                     None,
                                                     None,
                                                     None,
                                                     None,
                                                     None,
                                                     None,
                                                     None,
                                                     None,
                                                     local_volume_links)
