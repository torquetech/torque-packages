# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import codecs
import functools
import json
import os
import shutil
import subprocess
import time
import threading

import jinja2
import yaml

from torque import v1

from demo import providers
from demo import types
from demo import utils


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

    if isinstance(obj, utils.Future):
        return _process_futures(obj.get())

    if callable(obj):
        return _process_futures(obj())

    return obj


class Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "registry": {
                "server": "index.docker.io",
                "namespace": "user"
            }
        },
        "schema": {
            "registry": {
                "server": str,
                "namespace": str
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._images = []
        self._targets = {}
        self._load_balancer = False

        self._lock = threading.Lock()

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

    def _push_images(self):
        """TODO"""

        cmd = [
            "docker", "login",
            self.configuration["registry"]["server"]
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       cwd=self.context.path(),
                       check=True)

        ns = self.namespace()

        for image in self._images:
            if ns:
                namespaced_image = f"{self.namespace()}/{image}"

                cmd = [
                    "docker", "tag",
                    image, namespaced_image
                ]

                print(f"+ {' '.join(cmd)}")
                subprocess.run(cmd,
                               env=os.environ,
                               cwd=self.context.path(),
                               check=True)

            cmd = [
                "docker", "push",
                namespaced_image
            ]

            print(f"+ {' '.join(cmd)}")
            subprocess.run(cmd,
                           env=os.environ,
                           cwd=self.context.path(),
                           check=True)

    def _apply_targets(self):
        """TODO"""

        target_path = f"{self.context.path()}/helm"

        try:
            shutil.rmtree(target_path)

        except FileNotFoundError:
            pass

        os.makedirs(f"{target_path}/templates")

        targets = _process_futures(self._targets)

        chart = {
            "apiVersion": "v2",
            "name": utils.normalize(self.context.deployment_name),
            "type": "application",
            "version": "0.1.0",
            "appVersion": "1.16.0"
        }

        for name, target in targets.items():
            with open(f"{target_path}/templates/{name}.yaml", "w", encoding="utf8") as file:
                objs = [
                    yaml.safe_dump(obj, sort_keys=False) for obj in target
                ]

                file.write("---\n".join(objs))

        with open(f"{target_path}/Chart.yaml", "w", encoding="utf8") as file:
            file.write(yaml.safe_dump(chart, sort_keys=False))

    def _print_info(self):
        """TODO"""

        if not self._load_balancer:
            return

        retrys = 10

        while retrys != 0:
            cmd = [
                "kubectl", "get",
                "-o", "json",
                "--namespace", "ingress-nginx",
                "service/ingress-nginx-controller"
            ]

            print(f"+ {' '.join(cmd)}")
            p = subprocess.run(cmd,
                               env=os.environ,
                               cwd=self.context.path(),
                               check=True,
                               capture_output=True)

            ingress_ctrl = json.loads(p.stdout.decode("utf8"))

            try:
                lb = ingress_ctrl["status"]["loadBalancer"]

                ingress = lb["ingress"][0]
                lb_host = ingress["hostname"]

                break

            except IndexError:
                pass

            except KeyError:
                pass

            time.sleep(1)
            retrys -= 1

        if retrys == 0:
            return

        print("\n" f"Load balancer: http://{lb_host}")

    def _apply(self):
        """TODO"""

        self._apply_targets()
        self._push_images()

        cmd = [
            "helm", "upgrade",
            "-i", utils.normalize(self.context.deployment_name), "helm",
            "--debug"
        ]

        print(f"+ {' '.join(cmd)}")
        print(self.context.path())
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=True)

        self._print_info()

    def _delete(self):
        """TODO"""

        cmd = [
            "helm", "uninstall",
            utils.normalize(self.context.deployment_name),
            "--debug"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=False)

    def namespace(self) -> str:
        """TODO"""

        return self.configuration["registry"]["namespace"]

    def add_image(self, image: str):
        """TODO"""

        with self._lock:
            self._images.append(image)

    def add_load_balancer(self) -> bool:
        """TODO"""

        with self._lock:
            if self._load_balancer:
                raise RuntimeError("multiple load balancers not supported")

            self._load_balancer = True

    def add_to_target(self, name: str, objs: [dict]):
        """TODO"""

        with self._lock:
            if name not in self._targets:
                self._targets[name] = []

            self._targets[name] += objs


class Images(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Images

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            }
        }

    def push(self, image: str) -> str:
        """TODO"""

        self.interfaces.k8s.add_image(image)

        ns = self.interfaces.k8s.namespace()

        if ns:
            return f"{ns}/{image}"

        return image


class Secrets(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Secrets

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            }
        }

    @staticmethod
    def encode_b64(string: str) -> str:
        """TODO"""

        string = bytes(string, encoding="utf8")
        string = codecs.encode(string, "base64")
        string = str(string, encoding="utf8")

        return string.strip()

    def _k8s_create(self, name: str, entries: [types.KeyValue]) -> dict:
        """TODO"""

        name = utils.normalize(name)

        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name
            },
            "data": {
                entry.key: self.encode_b64(entry.value)
                for entry in entries
            },
            "type": "Opaque"
        }

    def create(self, name: str, entries: [types.KeyValue]) -> utils.Future[object]:
        """TODO"""

        self.interfaces.k8s.add_to_target(f"component_{name}", [
            self._k8s_create(name, entries)
        ])

        return utils.Future(name)


class Services(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Services

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            }
        }

    def _k8s_create(self, name: str, type: str, port: int, target_port: int) -> dict:
        """TODO"""

        name = utils.normalize(name)

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
                "ports": [{
                    "protocol": type.upper(),
                    "port": port,
                    "targetPort": target_port
                }]
            }
        }

    def create(self, name: str, type: str, port: int, target_port: int) -> utils.Future[object]:
        """TODO"""

        self.interfaces.k8s.add_to_target(f"component_{name}", [
            self._k8s_create(name, type, port, target_port),
        ])

        return utils.Future((type.lower(), name, port))


class Deployments(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.Deployments

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            }
        }

    def _convert_environment(self, env: [types.KeyValue]) -> [dict]:
        """TODO"""

        if not env:
            return []

        return [{
            "name": entry.key,
            "value": entry.value
        } for entry in env]

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
                        "name": utils.normalize(link.object.get()),
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
            "name": utils.normalize(link.name),
            "mountPath": link.mount_path
        } for link in volume_links]

        def resolve_future(link: types.VolumeLink) -> dict:
            return {
                "name": utils.normalize(link.name),
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

        name = utils.normalize(name)

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
                    "matchLabels": {
                        "app": name
                    }
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
                        "volumes": volumes,
                        "securityContext": {
                            "runAsUser": 0
                        }
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

        self.interfaces.k8s.add_to_target(f"component_{name}", [
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


class PersistentVolumes(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.PersistentVolumes

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            },
            "vol": {
                "interface": providers.PersistentVolumesProvider,
                "required": True
            }
        }

    def create(self, name: str, size: int) -> utils.Future[object]:
        """TODO"""

        return utils.Future({
            "name": utils.normalize(name),
            "awsElasticBlockStore": {
                "volumeID": self.interfaces.vol.create(name, size),
                "fsType": "ext4"
            }
        })


class HttpLoadBalancers(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.HttpLoadBalancers

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self):
        """TODO"""

        self.interfaces.k8s.add_load_balancer()

        templates = utils.load_file(f"{utils.module_path()}/templates/http_lb.yaml.template")
        templates = templates.split("---")

        templates = map(jinja2.Template, templates)

        for template in templates:
            self.interfaces.k8s.add_to_target("k8s_http_load_balancer",
                                        [yaml.safe_load(template.render())])


class HttpIngressLinks(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.HttpIngressLinks

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": Provider,
                "required": True
            }
        }

    def _convert_network_link(self, path: str, network_link: types.NetworkLink) -> dict:
        """TODO"""

        def resolve_future() -> list:
            link = network_link.object.get()

            return [{
                "http": {
                    "paths": [{
                        "pathType": "Prefix",
                        "path": path,
                        "backend": {
                            "service": {
                                "name": utils.normalize(link[1]),
                                "port": {
                                    "number": link[2]
                                }
                            }
                        }
                    }]
                }
            }]

        return resolve_future

    def _k8s_create(self, name: str, path: str, network_link: types.NetworkLink):
        """TODO"""

        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{utils.normalize(name)}",
            },
            "spec": {
                "ingressClassName": "nginx",
                "rules": self._convert_network_link(path, network_link)
            }
        }

    def create(self, name: str, path: str, network_link: types.NetworkLink):
        """TODO"""

        self.interfaces.k8s.add_to_target(f"component_{name}", [
            self._k8s_create(name, path, network_link)
        ])
