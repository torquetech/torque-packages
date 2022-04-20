# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import yaml

from torque import v1

from demo import providers
from demo import utils


class ImagesProvider(providers.ImagesProvider):
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

    def on_apply(self):
        """TODO"""


class SecretsProvider(providers.SecretsProvider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._targets = {}

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def _add_to_target(self, name: str, objs: [object]):
        """TODO"""

        if name not in self._targets:
            self._targets[name] = []

        self._targets[name] += objs

    def _k8s_create(self, name: str, entries: [providers.KeyValue]) -> object:
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

    def create(self, name: str, entries: [providers.KeyValue]) -> v1.utils.Future[object]:
        """TODO"""

        self._add_to_target(name, [
            self._k8s_create(name, entries)
        ])

        return v1.utils.Future(name)

    def on_apply(self):
        """TODO"""

        for name, target in self._targets.items():
            with open(f"{self.metadata.path}/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))

class ServicesProvider(providers.ServicesProvider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._targets = {}

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def _add_to_target(self, name: str, objs: [object]):
        """TODO"""

        if name not in self._targets:
            self._targets[name] = []

        self._targets[name] += objs

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

        self._add_to_target(name, [
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

    def on_apply(self):
        """TODO"""

        for name, target in self._targets.items():
            with open(f"{self.metadata.path}/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))


class DeploymentsProvider(providers.DeploymentsProvider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._targets = {}

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    def _add_to_target(self, name: str, objs: [object]):
        """TODO"""

        if name not in self._targets:
            self._targets[name] = []

        self._targets[name] += objs

    def _convert_network_links(self, network_links: [providers.NetworkLink]) -> [object]:
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

    def _convert_secret_links(self, secret_links: [providers.SecretLink]) -> [object]:
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

    def _k8s_create(self,
                    name: str,
                    image: str,
                    cmd: [str],
                    args: [str],
                    cwd: str,
                    env: [providers.KeyValue],
                    network_links: [providers.NetworkLink],
                    volume_links: [providers.VolumeLink],
                    secret_links: [providers.SecretLink],
                    replicas: int) -> object:
        """TODO"""

        env = [{"name": e.key, "value": e.value} for e in env]
        env += self._convert_secret_links(secret_links)
        env += self._convert_network_links(network_links)

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
                            "env": env
                        }]
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
               env: [providers.KeyValue],
               network_links: [providers.NetworkLink],
               volume_links: [providers.VolumeLink],
               secret_links: [providers.SecretLink],
               replicas: int):
        """TODO"""

        self._add_to_target(name, [
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

    def on_apply(self):
        """TODO"""

        for name, target in self._targets.items():
            with open(f"{self.metadata.path}/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))
