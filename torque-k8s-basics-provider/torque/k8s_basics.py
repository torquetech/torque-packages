# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from torque import basics
from torque import k8s
from torque import k8s_volumes
from torque import v1


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""


class V1TaskImplementation(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = basics.V1TaskImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "environment": {}
        },
        "schema": {
            "environment": {
                v1.schema.Optional(str): str
            },
            v1.schema.Optional("volume"): str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "k8s": {
                "interface": k8s.V1Provider,
                "required": True
            },
            "vol": {
                "interface": k8s_volumes.V1Interface,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._environment = []
        self._image_tag = None
        self._image_id = None
        self._command = None
        self._arguments = None
        self._working_directory = None

        with self.interfaces.k8s as p:
            p.add_hook("apply-objects", self._task_apply)

    def _task_apply(self):
        """DOCSTRING"""

        namespace = self.interfaces.k8s.namespace()
        image_tag = self.interfaces.k8s.register_image(self._image_tag, namespace)

        obj = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.name,
                "namespace": namespace,
                "labels": {
                    "app.kubernetes.io/name": self.name
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": self.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app.kubernetes.io/name": self.name
                        },
                        "annotations": {
                            "torquetech.io/image-id": self._image_id
                        }
                    },
                    "spec": {
                        "restartPolicy": "Always",
                        "containers": [{
                            "name": "main",
                            "image": image_tag
                        }],
                        "imagePullSecrets": [{
                            "name": "registry"
                        }]
                    }
                }
            }
        }

        spec = obj["spec"]["template"]["spec"]
        container = spec["containers"][0]

        if self._command:
            container["command"] = self._command

        if self._arguments:
            container["args"] = self._arguments

        if self._working_directory:
            container["workDir"] = self._working_directory

        container["env"] = [{
            "name": name,
            "value": value
        } for name, value in self.configuration["environment"].items()]

        container["env"].extend([{
            "name": name,
            "value": value
        } for name, value in self._environment])

        path = self.configuration.get("volume")

        if path:
            if not self.interfaces.vol:
                raise v1.exceptions.RuntimeError(f"{self.name}: no volumes provider")

            container["volumeMounts"] = [{
                "name": self.interfaces.vol.ref_name(),
                "mountPath": path
            }]

            spec["volumes"] = [
                self.interfaces.vol.spec()
            ]

        self.interfaces.k8s.add_object(obj)

    def add_environment(self, name: str, value: v1.utils.Future[str] | str):
        """DOCSTRING"""

        self._environment.append((name, value))

    def set_image(self, tag: str, id: str):
        """DOCSTRING"""

        self._image_tag = tag
        self._image_id = id

    def set_command(self, command: [str]):
        """DOCSTRING"""

        self._command = command

    def set_arguments(self, arguments: [str]):
        """DOCSTRING"""

        self._arguments = arguments

    def set_working_directory(self, working_directory: str):
        """DOCSTRING"""

        self._working_directory = working_directory


class V1ServiceImplementation(V1TaskImplementation):
    """DOCSTRING"""

    IMPLEMENTS = basics.V1ServiceImplementationInterface

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = None
        self._port = None

        with self.interfaces.k8s as p:
            p.add_hook("apply-objects", self._svc_apply)

    def _svc_apply(self) -> str:
        """DOCSTRING"""

        namespace = self.interfaces.k8s.namespace()

        obj = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self.name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app.kubernetes.io/name": self.name
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": int(self._port),
                    "targetPort": int(self._port)
                }]
            }
        }

        self.interfaces.k8s.add_object(obj)

    def set_proto(self, proto: str):
        """DOCSTRING"""

        self._proto = proto

    def set_port(self, port: int):
        """DOCSTRING"""

        self._port = port

    def service(self) -> v1.utils.Future[basics.Service]:
        """DOCSTRING"""

        host = f"{self.name}.{self.interfaces.k8s.namespace()}"

        return v1.utils.Future(basics.Service(self._proto, host, self._port))


repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1TaskImplementation,
            V1ServiceImplementation
        ]
    }
}
