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
from demo import utils


LoadBalancerLink = collections.namedtuple("LoadBalancerLink", [
    "service",
    "path",
    "port"
])


_LOAD_BALANCER_TEMPLATE = """server {
  listen 80;
  server_name localhost;
{%- for link in links %}

  location {{link.path}} {
    proxy_pass http://{{link.service}}:{{link.port}};
  }
{%- endfor %}
}
"""


class Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("workspace_path"): str
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._deployments = {}
        self._volumes = {}
        self._load_balancer = False
        self._load_balancer_links = []

        self._lock = threading.Lock()

        if "workspace_path" not in self.configuration:
            self.configuration["workspace_path"] = None

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

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
                "source": link.object.get(),
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

    def _generate_load_balancer(self, deployment_path: str):
        """TODO"""

        workspace_path = self.configuration["workspace_path"]

        service = {}

        if self._load_balancer:
            # pylint: disable=W0640

            conf_path = f"{deployment_path}/lb.conf"
            conf_path = conf_path[len(v1.utils.torque_root())+1:]

            with open(v1.utils.resolve_path(conf_path), "w", encoding="utf8") as file:
                template = jinja2.Template(_LOAD_BALANCER_TEMPLATE)
                file.write(template.render(links=self._load_balancer_links))

            if workspace_path is None:
                conf_path = v1.utils.resolve_path(conf_path)

            else:
                conf_path = os.path.join(workspace_path, conf_path)
                conf_path = os.path.normpath(conf_path)

            service["torque-lb"] = {
                "image": "nginx:stable",
                "ports": [f"{self._load_balancer}:80"],
                "volumes": [{
                    "type": "bind",
                    "source": conf_path,
                    "target": "/etc/nginx/conf.d/default.conf"
                }]
            }

        return service

    def _print_info(self):
        """TODO"""

        print("\nComponent ip addresses:\n")

        cmd = [
            "docker", "compose", "ps",
            "--status", "running",
            "--format", "json"
        ]

        p = subprocess.run(cmd,
                           env=os.environ,
                           cwd=self.context.path(),
                           check=True,
                           capture_output=True)

        containers = json.loads(p.stdout.decode("utf8"))

        for container in containers:
            name = container["Name"]

            deployment = self.context.deployment_name
            deployment = deployment.replace(".", "")

            cmd = [
                "docker", "inspect",
                f"--format={{{{.NetworkSettings.Networks.{deployment}_default.IPAddress}}}}",
                name
            ]

            p = subprocess.run(cmd,
                               env=os.environ,
                               cwd=self.context.path(),
                               check=True,
                               capture_output=True)

            ip = p.stdout.decode("utf8").strip()

            if ip:
                name = name.split("-")[1]

                if name.startswith("lb."):
                    name = name[3:]

                name += ":"

                print(f"{name:25} {ip}")

        if self._load_balancer:
            print("\n" f"Load balancer: http://localhost:{self._load_balancer}")

    def _apply(self):
        """TODO"""

        deployments = self._deployments | \
            self._generate_load_balancer(self.context.path())

        compose = {
            "services": deployments,
            "volumes": self._volumes
        }

        with open(f"{self.context.path()}/docker-compose.yaml", "w", encoding="utf8") as file:
            file.write(yaml.safe_dump(compose, sort_keys=False))

        cmd = [
            "docker", "compose", "up",
            "-d", "--remove-orphans"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=True)

        self._print_info()

    def _delete(self):
        """TODO"""

        cmd = [
            "docker", "compose", "down",
            "--volumes"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=False)

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

    def add_load_balancer(self, port: int):
        """TODO"""

        with self._lock:
            if self._load_balancer:
                raise RuntimeError("multiple load balancers not supported")

            self._load_balancer = port

    def add_load_balancer_link(self, path: str, network_link: types.NetworkLink):
        """TODO"""

        link = network_link.object.get()

        service = link[1]
        port = link[2]

        with self._lock:
            self._load_balancer_links.append(LoadBalancerLink(service, path, port))


class Images(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Images

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def push(self, image: str) -> str:
        """TODO"""

        return image


class Secrets(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Secrets

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self, name: str, entries: [types.KeyValue]) -> utils.Future[object]:
        """TODO"""

        return utils.Future(entries)


class Services(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Services

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self, name: str, type: str, port: int, target_port: int) -> utils.Future[object]:
        """TODO"""

        return utils.Future((type.lower(), name, port))


class Deployments(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Deployments

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

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

        self.interfaces.dc.add_deployment(name,
                                          image,
                                          cmd,
                                          cwd,
                                          env,
                                          network_links,
                                          volume_links,
                                          secret_links,
                                          [])


class Development(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Development

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

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

        self.interfaces.dc.add_deployment(name,
                                          image,
                                          cmd,
                                          cwd,
                                          env,
                                          network_links,
                                          volume_links,
                                          secret_links,
                                          local_volume_links)


class PersistentVolumes(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.PersistentVolumes

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self, name: str, size: int) -> utils.Future[object]:
        """TODO"""

        self.interfaces.dc.add_volume(name)

        return utils.Future(name)


class PersistentVolumesProvider(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.PersistentVolumesProvider

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self, name: str, size: int) -> utils.Future[str]:
        """TODO"""

        return utils.Future("<ignored_value>")


class HttpLoadBalancers(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.HttpLoadBalancers

    CONFIGURATION = {
        "defaults": {
            "port": 8080
        },
        "schema": {
            "port": int
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self):
        """TODO"""

        self.interfaces.dc.add_load_balancer(self.configuration["port"])


class HttpIngressLinks(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.HttpIngressLinks

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self, name: str, path: str, network_link: types.NetworkLink):
        """TODO"""

        self.interfaces.dc.add_load_balancer_link(path, network_link)
