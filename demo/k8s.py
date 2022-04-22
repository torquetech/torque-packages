# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading
import yaml

from torque import v1

from demo import interfaces
from demo import types


class ImagesInterface(interfaces.ImagesInterface):
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

    def push(self, image: str):
        """TODO"""


class SecretsInterface(interfaces.SecretsInterface):
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

    def _k8s_create(self, name: str, entries: [types.KeyValue]) -> object:
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

        self.provider.add_to_target(name, [
            self._k8s_create(name, entries)
        ])

        return v1.utils.Future(name)


class ServicesInterface(interfaces.ServicesInterface):
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

    def _k8s_create(self, name: str, tcp_ports: [int], udp_ports: [int]) -> object:
        """TODO"""

        ports = []

        if tcp_ports:
            ports += [{"protocol": "TCP", "port": port} for port in tcp_ports]

        if udp_ports:
            ports += [{"protocol": "UDP", "port": port} for port in udp_ports]

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
                "ports": ports
            }
        }

    def create(self, name: str, tcp_ports: [int], udp_ports: [int]) -> v1.utils.Future[object]:
        """TODO"""

        self.provider.add_to_target(name, [
            self._k8s_create(name, tcp_ports, udp_ports),
        ])

        uris = []

        if tcp_ports:
            uris += [
                f"tcp://{name}:{port}" for port in tcp_ports
            ]

        if udp_ports:
            uris += [
                f"udp://{name}:{port}" for port in udp_ports
            ]

        return v1.utils.Future(uris)


class DeploymentsInterface(interfaces.DeploymentsInterface):
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

    def _convert_network_links(self, network_links: [types.NetworkLink]) -> [object]:
        """TODO"""

        if not network_links:
            return []

        env = []

        for link in network_links:
            ndx = 0
            name = link.name.upper()

            for uri in link.object.get():
                env.append({
                    "name": f"{name}_LINK_{ndx}",
                    "value": f"{uri}"
                })

                ndx += 1

        return env

    def _convert_secret_links(self, secret_links: [types.SecretLink]) -> [object]:
        """TODO"""

        if not secret_links:
            return []

        return [{
            "name": secret_link.name,
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret_link.object.get(),
                    "key": secret_link.key
                }
            }
        } for secret_link in secret_links]

    def _convert_volume_links(self, volume_links: [types.VolumeLink]) -> ([object], [object]):
        """TODO"""

        if not volume_links:
            return None, None

        mounts = [{
            "name": volume_link.name,
            "mountPath": volume_link.mount_path
        } for volume_link in volume_links]

        volumes = [{
            "name": volume_link.name,
            **volume_link.object.get(),
        } for volume_link in volume_links]

        return mounts, volumes

    def _k8s_create(self,
                    name: str,
                    image: str,
                    cmd: [str],
                    args: [str],
                    cwd: str,
                    env: [types.KeyValue],
                    network_links: [types.NetworkLink],
                    volume_links: [types.VolumeLink],
                    secret_links: [types.SecretLink],
                    replicas: int) -> object:
        """TODO"""

        env = [{"name": e.key, "value": e.value} for e in env]
        env += self._convert_secret_links(secret_links)
        env += self._convert_network_links(network_links)

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
                "replicas": replicas,
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
               network_links: [types.NetworkLink],
               volume_links: [types.VolumeLink],
               secret_links: [types.SecretLink],
               replicas: int):
        """TODO"""

        self.provider.add_to_target(name, [
            self._k8s_create(name,
                             image,
                             cmd,
                             args,
                             cwd,
                             env,
                             network_links,
                             volume_links,
                             secret_links,
                             replicas)
        ])


class ConfigMapsInterface(interfaces.ConfigMapsInterface):
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

    def _k8s_create(self, name: str, configuration: object) -> object:
        """TODO"""

        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name
            },
            "data": configuration
        }

    def create(self, name: str, configuration: object) -> v1.utils.Future[object]:
        """TODO"""

        self.provider.add_to_target(name, [
            self._k8s_create(name, configuration)
        ])

        return v1.utils.Future({
            "configMap": {
                "name": name
            }
        })


class EBSVolumesInterface(interfaces.EBSVolumesInterface):
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

    def create(self, name: str, volume_id: str) -> v1.utils.Future[object]:
        """TODO"""

        return v1.utils.Future({
            "name": name,
            "awsElasticBlockStore": {
                "volumeID": volume_id,
                "fsType": "ext4"
            }
        })


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "namespace": "test"
        },
        "schema": {
            "namespace": str
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._targets = {}
        self._lock = threading.Lock()

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        for name, target in self._targets.items():
            with open(f"{deployment.path}/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))

    def on_delete(self, deployment: str):
        """TODO"""

    def add_to_target(self, name: str, objs: [object]):
        """TODO"""

        with self._lock:
            if name not in self._targets:
                self._targets[name] = []

            self._targets[name] += objs
