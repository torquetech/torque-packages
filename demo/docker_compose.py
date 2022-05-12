# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import collections
import json
import os
import subprocess
import threading

import jinja2
import yaml

from torque import v1

from demo import providers
from demo import types


LoadBalancer = collections.namedtuple("LoadBalancer", [
    "host",
    "port"
])

LoadBalancerLink = collections.namedtuple("LoadBalancerLink", [
    "name",
    "host",
    "path",
    "service",
    "port"
])


_LOAD_BALANCER_TEMPLATE = """server {
  listen 80;
  server_name {{host}};
{%- for link in links %}

  location {{link.path}} {
    proxy_pass http://{{link.service}}:{{link.port}};
  }
{%- endfor %}
}
"""


class Images(providers.Images):
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

    def push(self, image: str) -> str:
        """TODO"""

        return image


class Secrets(providers.Secrets):
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
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
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
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
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
               secret_links: [types.SecretLink]):
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
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
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
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
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
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {}

    def create(self, name: str, size: int) -> v1.utils.Future[str]:
        """TODO"""

        return v1.utils.Future("<ignored_value>")


class HttpLoadBalancers(providers.HttpLoadBalancers):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "port": 8080
        },
        "schema": {
            "port": int
        }
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

    def create(self, name: str, host: str):
        """TODO"""

        self.provider.add_load_balancer(name, host, self.configuration["port"])


class HttpIngressLinks(providers.HttpIngressLinks):
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

    def create(self,
               name: str,
               host: str,
               path: str,
               network_link: types.NetworkLink):
        """TODO"""

        self.provider.add_load_balancer_link(name, host, path, network_link)


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("workspace_path"): str
        }
    }

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._deployments = {}
        self._volumes = {}
        self._load_balancers = {}
        self._load_balancer_links = []

        self._lock = threading.Lock()

        if "workspace_path" not in self.configuration:
            self.configuration["workspace_path"] = None

    def _convert_environment(self, env: [types.KeyValue]) -> [dict]:
        """TODO"""

        if not env:
            return []

        return [
            f"{e.key}={e.value}" for e in env
        ]

    def _convert_network_links(self, network_links: [types.NetworkLink]) -> [dict]:
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

    def _convert_secret_links(self, secret_links: [types.SecretLink]) -> [dict]:
        """TODO"""

        if not secret_links:
            return []

        env = []

        for link in secret_links:
            name = link.name
            key = link.key
            link = link.object.get()

            for el in link:
                if el.key == key:
                    env.append(f"{name}={el.value}")

        return env

    def _convert_volume_links(self, volume_links: [types.VolumeLink]) -> [dict]:
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

    def _convert_local_volume_links(self, local_volume_links: [types.VolumeLink]) -> [dict]:
        """TODO"""

        if not local_volume_links:
            return []

        workspace_path = self.configuration["workspace_path"]

        volumes = []

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

    def _generate_load_balancers(self, deployment_path: str):
        """TODO"""

        workspace_path = self.configuration["workspace_path"]

        services = {}

        for name, lb in self._load_balancers.items():
            # pylint: disable=W0640

            conf_path = f"{deployment_path}/lb.{name}.conf"
            conf_path = conf_path[len(v1.utils.torque_root())+1:]

            with open(v1.utils.resolve_path(conf_path), "w", encoding="utf8") as file:
                links = filter(lambda x: x.host == lb.host, self._load_balancer_links)

                template = jinja2.Template(_LOAD_BALANCER_TEMPLATE)
                file.write(template.render(host=lb.host, links=links))

            if workspace_path is None:
                conf_path = v1.utils.resolve_path(conf_path)

            else:
                conf_path = os.path.join(workspace_path, conf_path)
                conf_path = os.path.normpath(conf_path)

            services[f"lb.{name}"] = {
                "image": "nginx:stable",
                "ports": [f"{lb.port}:80"],
                "volumes": [{
                    "type": "bind",
                    "source": conf_path,
                    "target": "/etc/nginx/conf.d/default.conf"
                }]
            }

        return services

    def _print_info(self, deployment: v1.deployment.Deployment):
        """TODO"""

        print("\nComponent ip addresses:\n")

        cmd = [
            "docker", "compose", "ps",
            "--status", "running",
            "--format", "json"
        ]

        p = subprocess.run(cmd,
                           env=os.environ,
                           cwd=deployment.path,
                           check=True,
                           capture_output=True)

        containers = json.loads(p.stdout.decode("utf8"))

        for container in containers:
            name = container["Name"]

            cmd = [
                "docker", "inspect",
                "--format={{.NetworkSettings.Networks.local_default.IPAddress}}",
                name
            ]

            p = subprocess.run(cmd,
                               env=os.environ,
                               cwd=deployment.path,
                               check=True,
                               capture_output=True)

            ip = p.stdout.decode("utf8").strip()

            if ip:
                name = name.split("-")[1]

                if name.startswith("lb."):
                    name = name[3:]

                name += ":"

                print(f"{name:30} {ip}")

        print("\nLoad balancers:\n")

        for name, lb in self._load_balancers.items():
            name = f"{name} ({lb.host}):"
            print(f"{name:30} http://localhost:{lb.port}")

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        deployments = self._deployments | self._generate_load_balancers(deployment.path)

        compose = {
            "services": deployments,
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

        self._print_info(deployment)

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

    def add_load_balancer(self, name: str, host: str, port: int):
        """TODO"""

        with self._lock:
            if any([i.host == host for i in self._load_balancers.values()]):
                raise RuntimeError(f"{host}: load balancer already exists")

            if any([i.port == port for i in self._load_balancers.values()]):
                raise RuntimeError(f"{port}: duplicate load balancer port")

            self._load_balancers[name] = LoadBalancer(host, port)

    def add_load_balancer_link(self,
                               name: str,
                               host: str,
                               path: str,
                               network_link: types.NetworkLink):
        """TODO"""

        link = network_link.object.get()

        service = link[1]
        port = link[2]

        with self._lock:
            self._load_balancer_links.append(LoadBalancerLink(name,
                                                              host,
                                                              path,
                                                              service,
                                                              port))
