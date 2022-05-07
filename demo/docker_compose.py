# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import threading

import jinja2
import yaml

from torque import v1

from demo import providers
from demo import types
from demo import utils


class Images(providers.Images):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def push(self, image: str):
        """TODO"""


class Secrets(providers.Secrets):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self, name: str, entries: [types.KeyValue]) -> v1.utils.Future[object]:
        """TODO"""

        return v1.utils.Future(entries)


class Services(providers.Services):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self, name: str, type: str, port: int, target_port: int) -> v1.utils.Future[object]:
        """TODO"""

        return v1.utils.Future((type.lower(), name, port))


class Deployments(providers.Deployments):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self,
               name: str,
               image: str,
               cmd: [str],
               args: [str],
               cwd: str,
               env: [types.KeyValue],
               ports: [types.Port],
               network_links: [types.NetworkLink],
               volume_links: [types.VolumeLink],
               secret_links: [types.SecretLink],
               replicas: int):
        """TODO"""

        if args:
            if cmd:
                cmd += args

            else:
                cmd = args

        self.provider.add_deployment(name,
                                     image,
                                     cmd,
                                     cwd,
                                     env,
                                     network_links,
                                     volume_links,
                                     secret_links,
                                     [])


class Development(providers.Development):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create_deployment(self,
                          name: str,
                          image: str,
                          cmd: [str],
                          args: [str],
                          cwd: str,
                          env: [types.KeyValue],
                          ports: [types.Port],
                          network_links: [types.NetworkLink],
                          volume_links: [types.VolumeLink],
                          secret_links: [types.SecretLink],
                          local_volume_links: [types.VolumeLink]):
        """TODO"""

        if args:
            if cmd:
                cmd += args

            else:
                cmd = args

        self.provider.add_deployment(name,
                                     image,
                                     cmd,
                                     cwd,
                                     env,
                                     network_links,
                                     volume_links,
                                     secret_links,
                                     local_volume_links)


class PersistentVolumes(providers.PersistentVolumes):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self, name: str, volume_id: str) -> v1.utils.Future[object]:
        """TODO"""

        self.provider.add_volume(name)

        return v1.utils.Future(volume_id)


class PersistentVolumesProvider(providers.PersistentVolumesProvider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self, name: str, size: int) -> v1.utils.Future[str]:
        """TODO"""

        return v1.utils.Future("<ignored_value>")


class HttpLoadBalancers(providers.HttpLoadBalancers):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._created = False

    def create(self, name: str, host: str):
        """TODO"""

        if self._created:
            return

        self._created = True


class HttpIngressLinks(providers.HttpIngressLinks):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def create(self,
               name: str,
               host: str,
               path: str,
               network_link: types.NetworkLink):
        """TODO"""


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("workspace_path"): str
        }
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._deployments = {}
        self._volumes = {}

        self._lock = threading.Lock()

    def _convert_environment(self, env: [types.KeyValue]) -> [object]:
        """TODO"""

        if not env:
            return []

        return [
            f"{e.key}={e.value}" for e in env
        ]

    def _convert_network_links(self, network_links: [types.NetworkLink]) -> [object]:
        """TODO"""

        if not network_links:
            return []

        env = []

        for link in network_links:
            name = link.name.upper()
            link = link.object.get()

            env.append(
                f"{name}_LINK={link[0]}://{link[1]}:{link[2]}"
            )

        return env

    def _convert_secret_links(self, secret_links: [types.SecretLink]) -> [object]:
        """TODO"""

        if not secret_links:
            return []

        env = []

        for link in secret_links:
            name = link.name
            key = link.key
            link = link.object.get()

            for l in link:
                if l.key == key:
                    env.append(
                        f"{name}={l.value}"
                    )

        return env

    def _convert_volume_links(self, volume_links: [types.VolumeLink]) -> [object]:
        """TODO"""

        if not volume_links:
            return []

        volumes = []

        for link in volume_links:
            volumes.append({
                "type": "volume",
                "source": link.name,
                "target": link.mount_path,
                "volume": {
                    "nocopy": True
                }
            })

        return volumes

    def _convert_local_volume_links(self, local_volume_links: [types.VolumeLink]) -> [object]:
        """TODO"""

        if not local_volume_links:
            return []

        volumes = []

        if "workspace_path" in self.configuration:
            workspace_path = self.configuration["workspace_path"]

        else:
            workspace_path = None

        for link in local_volume_links:
            if workspace_path is None:
                path = v1.utils.resolve_path(link.object.get())

            else:
                path = os.path.join(workspace_path, link.object.get())
                path = os.path.normpath(path)

            volumes.append({
                "type": "bind",
                "source": path,
                "target": link.mount_path
            })

        return volumes

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        compose = {
            "services": self._deployments,
            "volumes": self._volumes
        }

        with open(f"{deployment.path}/docker-compose.yaml", "w", encoding="utf8") as file:
            file.write(yaml.safe_dump(compose, sort_keys=False))

        if deployment.dry_run:
            return

        cmd = [
            "docker", "compose", "up",
            "-d", "--remove-orphans"
        ]

        subprocess.run(cmd, env=os.environ, cwd=deployment.path, check=True)

    def on_delete(self, deployment: v1.deployment.Deployment):
        """TODO"""

        if deployment.dry_run:
            return

        cmd = [
            "docker", "compose", "down",
            "--volumes"
        ]

        subprocess.run(cmd, env=os.environ, cwd=deployment.path, check=True)

    def add_volume(self, name: str):
        """TODO"""

        with self._lock:
            self._volumes[name] = None

    def add_deployment(self,
                       name: str,
                       image: str,
                       cmd: [str],
                       cwd: str,
                       env: [types.KeyValue],
                       network_links: [types.NetworkLink],
                       volume_links: [types.VolumeLink],
                       secret_links: [types.SecretLink],
                       local_volume_links: [types.VolumeLink]):
        """TODO"""

        env = self._convert_environment(env)
        env += self._convert_network_links(network_links)
        env += self._convert_secret_links(secret_links)

        volumes = self._convert_volume_links(volume_links)
        volumes += self._convert_local_volume_links(local_volume_links)

        deployment = {
            "image": image,
            "user": "root",
            "environment": env,
            "volumes": volumes
        }

        if cmd:
            deployment["command"] = cmd

        if cwd:
            deployment["working_dir"] = cwd

        with self._lock:
            self._deployments[name] = deployment
