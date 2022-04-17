# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import schema
import yaml

from torque import v1

from demo import interfaces
from demo import utils


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._targets = {}

    @classmethod
    def validate_configuration(cls, configuration: object) -> object:
        """TODO"""

        return utils.validate_schema("configuration",
                                     cls._CONFIGURATION,
                                     configuration)

    def _add_to_target(self, name: str, objs: [object]):
        """TODO"""

        if name not in self._targets:
            self._targets[name] = []

        self._targets[name] += objs

    def _k8s_create_secret(self,
                           name: str,
                           entries: [interfaces.Provider.KeyValue]) -> dict[str, object]:
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

    def _k8s_create_service(self, name: str, tcp_ports: [int], udp_ports: [int]) -> dict[str, object]:
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

    def _convert_secrets(self, secrets: [interfaces.Provider.Secret]) -> []:
        """TODO"""

        if not secrets:
            return []

        return [{
            "name": secret.env,
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret.obj.get(),
                    "key": secret.key
                }
            }
        } for secret in secrets]

    def _convert_network_links(self,
                               network_links: [interfaces.Provider.NetworkLink]) -> []:
        """TODO"""

        if not network_links:
            return []

        ndx = 0
        env = []

        for link in network_links:
            link = link.get()
            name = link.name.upper()

            if link.tcp_ports:
                for port in link.tcp_ports:
                    env.append({
                        "name": f"LINK_{name}_{ndx}",
                        "value": f"tcp:{port}:{link.host}"
                    })

                    ndx += 1

            if link.udp_ports:
                for port in link.udp_ports:
                    env.append({
                        "name": f"LINK_{name}_{ndx}",
                        "value": f"udp:{port}:{link.host}"
                    })

                    ndx += 1

        return env

    def _k8s_create_deployment(self,
                               name: str,
                               image: str,
                               cmd: [str],
                               args: [str],
                               cwd: str,
                               env: [interfaces.Provider.KeyValue],
                               network_links: [interfaces.Provider.NetworkLink],
                               volume_links: [object],
                               secrets: [interfaces.Provider.Secret],
                               replicas: int) -> dict[str, object]:
        """TODO"""

        env = [{"name": e.key, "value": e.value} for e in env]
        env += self._convert_secrets(secrets)
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

    def _push_image(self, image: str):
        """TODO"""

    def _create_secret(self,
                       name: str,
                       entries: [interfaces.Provider.KeyValue]) -> v1.interface.Future[str]:
        """TODO"""

        self._add_to_target(name, [
            self._k8s_create_secret(name, entries)
        ])

        return v1.interface.Future(name)

    def _create_deployment(self,
                           name: str,
                           image: str,
                           cmd: [str],
                           args: [str],
                           cwd: str,
                           env: [interfaces.Provider.KeyValue],
                           network_links: [interfaces.Provider.NetworkLink],
                           volume_links: [object],
                           secrets: [interfaces.Provider.Secret],
                           replicas: int):
        """TODO"""

        self._add_to_target(name, [
            self._k8s_create_deployment(name,
                                        image,
                                        cmd,
                                        args,
                                        cwd,
                                        env,
                                        network_links,
                                        volume_links,
                                        secrets,
                                        replicas)
        ])

    def _create_service(self,
                        name: str,
                        tcp_ports: [int],
                        udp_ports: [int]) -> v1.interface.Future[interfaces.Provider.NetworkLink]:
        """TODO"""

        self._add_to_target(name, [
            self._k8s_create_service(name, tcp_ports, udp_ports),
        ])

        return v1.interface.Future(interfaces.Provider.NetworkLink(name, name, tcp_ports, udp_ports))

    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return [
            interfaces.Provider(push_image=self._push_image,
                                create_secret=self._create_secret,
                                create_deployment=self._create_deployment,
                                create_service=self._create_service)
        ]

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        for name, target in self._targets.items():
            with open(f"{deployment.path}/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))
