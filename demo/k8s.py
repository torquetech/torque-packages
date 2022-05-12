# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
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

        self.provider.add_image(image)

        ns = self.provider.namespace()

        if ns:
            return f"{self.provider.namespace()}/{image}"

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

    def _k8s_create(self, name: str, entries: [types.KeyValue]) -> dict:
        """TODO"""

        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name
            },
            "data": {entry.key: entry.value for entry in entries},
            "type": "Opaque"
        }

    def create(self, name: str, entries: [types.KeyValue]) -> v1.utils.Future[object]:
        """TODO"""

        self.provider.add_to_target(f"component_{name}", [
            self._k8s_create(name, entries)
        ])

        return v1.utils.Future(name)


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

    def _k8s_create(self, name: str, type: str, port: int, target_port: int) -> dict:
        """TODO"""

        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name
            },
            "spec": {
                "selector": {
                    "app": name
                },
                "ports": {
                    "protocol": type.upper(),
                    "port": port,
                    "targetPort": target_port
                }
            }
        }

    def create(self, name: str, type: str, port: int, target_port: int) -> v1.utils.Future[object]:
        """TODO"""

        self.provider.add_to_target(f"component_{name}", [
            self._k8s_create(name, type, port, target_port),
        ])

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

    def _convert_environment(self, env: [types.KeyValue]) -> [dict]:
        """TODO"""

        if not env:
            return []

        return [
            {"name": e.key, "value": e.value} for e in env
        ]

    def _convert_network_links(self, network_links: [types.NetworkLink]) -> [dict]:
        """TODO"""

        if not network_links:
            return []

        def resolve_future(link: types.NetworkLink) -> dict:
            name = link.name.upper()
            link = link.object.get()

            return {
                "name": f"{name}_LINK",
                "value": f"{link[0]}://{link[1]}:{link[2]}"
            }

        return [
            functools.partial(resolve_future, link) for link in network_links
        ]

    def _convert_secret_links(self, secret_links: [types.SecretLink]) -> [dict]:
        """TODO"""

        if not secret_links:
            return []

        def resolve_future(link: types.SecretLink) -> dict:
            return {
                "name": link.name,
                "valueFrom": {
                    "secretKeyRef": {
                        "name": link.object.get(),
                        "key": link.key
                    }
                }
            }

        return [
            functools.partial(resolve_future, link) for link in secret_links
        ]

    def _convert_ports(self, ports: [types.Port]) -> [dict]:
        """TODO"""

        if not ports:
            return []

        return [{
            "name": port.name,
            "protocol": port.protocol.upper(),
            "containerPort": port.port
        } for port in ports]

    def _convert_volume_links(self, volume_links: [types.VolumeLink]) -> ([dict], [dict]):
        """TODO"""

        if not volume_links:
            return None, None

        mounts = [{
            "name": link.name,
            "mountPath": link.mount_path
        } for link in volume_links]

        def resolve_future(link: types.VolumeLink) -> dict:
            return {
                "name": link.name,
                **link.object.get(),
            }

        volumes = [
            functools.partial(resolve_future, link) for link in volume_links
        ]

        return mounts, volumes

    def _k8s_create(self,
                    name: str,
                    image: str,
                    cmd: [str],
                    args: [str],
                    cwd: str,
                    env: [types.KeyValue],
                    ports: [types.Port],
                    network_links: [types.NetworkLink],
                    volume_links: [types.VolumeLink],
                    secret_links: [types.SecretLink]) -> dict:
        """TODO"""

        env = self._convert_environment(env)
        env += self._convert_network_links(network_links)
        env += self._convert_secret_links(secret_links)

        ports = self._convert_ports(ports)

        mounts, volumes = self._convert_volume_links(volume_links)

        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "labels": {
                    "app": name
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "app": name
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "restartPolicy": "Always",
                        "containers": [{
                            "name": f"{name}-container",
                            "image": image,
                            "command": cmd,
                            "args": args,
                            "workingDir": cwd,
                            "env": env,
                            "ports": ports,
                            "volumeMounts": mounts
                        }],
                        "volumes": volumes
                    }
                }
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

        self.provider.add_to_target(f"component_{name}", [
            self._k8s_create(name,
                             image,
                             cmd,
                             args,
                             cwd,
                             env,
                             ports,
                             network_links,
                             volume_links,
                             secret_links)
        ])


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

        return {
            "vol": {
                "interface": providers.PersistentVolumesProvider,
                "required": True
            }
        }

    def create(self, name: str, size: int) -> v1.utils.Future[object]:
        """TODO"""

        return v1.utils.Future({
            "name": name,
            "awsElasticBlockStore": {
                "volumeID": self.binds.vol.create(name, size),
                "fsType": "ext4"
            }
        })


class HttpLoadBalancers(providers.HttpLoadBalancers):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._created = False

    def create(self, name: str, host: str):
        """TODO"""

        if self._created:
            return

        self._created = True

        templates = utils.load_file(f"{utils.module_path()}/templates/http_lb.yaml.template")
        templates = templates.split("---")

        templates = map(jinja2.Template, templates)

        for template in templates:
            self.provider.add_to_target("k8s_http_load_balancer",
                                        [yaml.safe_load(template.render())])


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

    def _convert_network_link(self,
                              host: str,
                              path: str,
                              network_link: types.NetworkLink) -> dict:
        """TODO"""

        def resolve_future() -> list:
            link = network_link.object.get()

            return [{
                "host": host,
                "http": {
                    "paths": {
                        "pathType": "Prefix",
                        "path": path,
                        "backend": {
                            "service": {
                                "name": link[1],
                                "port": {
                                    "number": link[2]
                                }
                            }
                        }
                    }
                }
            }]

        return resolve_future

    def _k8s_create(self,
                    name: str,
                    host: str,
                    path: str,
                    network_link: types.NetworkLink):
        """TODO"""

        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": name,
            },
            "spec": {
                "rules": self._convert_network_link(host, path, network_link)
            }
        }

    def create(self,
               name: str,
               host: str,
               path: str,
               network_link: types.NetworkLink):
        """TODO"""

        self.provider.add_to_target(f"component_{name}", [
            self._k8s_create(name, host, path, network_link)
        ])


def _process_futures(obj: object) -> object:
    """TODO"""

    if isinstance(obj, dict):
        return {
            k: _process_futures(v) for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            _process_futures(v) for v in obj
        ]

    if isinstance(obj, v1.utils.Future):
        return _process_futures(obj.get())

    if callable(obj):
        return _process_futures(obj())

    return obj


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "registry": {
                "server": "index.docker.io",
                "namespace": "user",
                "run_login": True
            }
        },
        "schema": {
            "registry": {
                "server": str,
                "namespace": str,
                "run_login": bool
            }
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

        self._images = []
        self._targets = {}
        self._lock = threading.Lock()

    def _push_images(self, deployment: v1.deployment.Deployment):
        """TODO"""

        if self.configuration["registry"]["run_login"]:
            cmd = [
                "docker", "login",
                self.configuration["registry"]["server"]
            ]

            subprocess.run(cmd,
                           env=os.environ,
                           cwd=deployment.path,
                           check=True)

        ns = self.namespace()

        for image in self._images:
            if ns:
                namespaced_image = f"{self.namespace()}/{image}"

                cmd = [
                    "docker", "tag",
                    image, namespaced_image
                ]

                subprocess.run(cmd,
                               env=os.environ,
                               cwd=deployment.path,
                               check=True)

            cmd = [
                "docker", "push",
                namespaced_image
            ]

            subprocess.run(cmd,
                           env=os.environ,
                           cwd=deployment.path,
                           check=True)

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        targets = _process_futures(self._targets)

        for name, target in targets.items():
            with open(f"{deployment.path}/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))

        if deployment.dry_run:
            return

        self._push_images(deployment)

    def on_delete(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def namespace(self) -> str:
        """TODO"""

        return self.configuration["registry"]["namespace"]

    def add_image(self, image: str):
        """TODO"""

        with self._lock:
            self._images.append(image)

    def add_to_target(self, name: str, objs: [dict]):
        """TODO"""

        with self._lock:
            if name not in self._targets:
                self._targets[name] = []

            self._targets[name] += objs
