# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import basics
from torque import container_registry
from torque import k8s
from torque import v1


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1Implementation(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = basics.V1ImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "environment": {},
            "volumes": {}
        },
        "schema": {
            "environment": {
                v1.schema.Optional(str): str
            },
            "volumes": {
                v1.schema.Optional(str): {
                    "path": str,
                    "size": str
                }
            },
            v1.schema.Optional("overrides"): object
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": k8s.V1Provider,
                "required": True
            },
            "cr": {
                "interface": container_registry.V1Provider,
                "required": True
            },
            "vol": {
                "interface": k8s.V1VolumeInterface,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sanitized_name = self.name.replace(".", "-")
        self._sanitized_name = self._sanitized_name.replace("_", "-")

    def create_task(self, image: str, **kwargs):
        """TODO"""

        image = self.interfaces.cr.push(image)

        obj = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self._sanitized_name,
                "namespace": self.interfaces.k8s.namespace(),
                "labels": {
                    "app.kubernetes.io/name": self._sanitized_name
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": self._sanitized_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app.kubernetes.io/name": self._sanitized_name
                        }
                    },
                    "spec": {
                        "restartPolicy": "Always",
                        "containers": [{
                            "name": "main",
                            "image": image
                        }],
                        "imagePullSecrets": [{
                            "name": "registry"
                        }]
                    }
                }
            }
        }

        command = kwargs.get("command")
        arguments = kwargs.get("arguments")
        environment = kwargs.get("environment")
        working_directory = kwargs.get("working_directory")

        spec = obj["spec"]["template"]["spec"]
        container = spec["containers"][0]

        if command:
            container["command"] = command

        if arguments:
            container["args"] = arguments

        if working_directory:
            container["workDir"] = working_directory

        container["env"] = [{
            "name": name.upper(),
            "value": value
        } for name, value in environment]

        container["env"].extend([{
            "name": name.upper(),
            "value": value
        } for name, value in self.configuration["environment"]])

        volumes = self.configuration["volumes"]

        if volumes:
            if not self.interfaces.vol:
                raise v1.exceptions.RuntimeError(f"{self.name}: no volumes provider")

            prefix = f"{self.context.deployment_name}-{self.name}"
            prefix = prefix.replace(".", "-")

            container["volumeMounts"] = [{
                "name": f"{prefix}-{name}",
                "mountPath": vol["path"]
            } for name, vol in volumes.items()]

            spec["volumes"] = [
                self.interfaces.vol.create(f"{prefix}-{name}", vol["size"])
                for name, vol in volumes.items()
            ]

        overrides = self.configuration.get("overrides", {})
        obj = v1.utils.merge_dicts(obj, overrides)

        self.interfaces.k8s.add_object(obj)

        namespace = obj["metadata"]["namespace"]
        self.interfaces.k8s.add_container_registry_to(namespace)

        return namespace

    def create_service(self, image: str, proto: str, port: str, **kwargs) -> str:
        """TODO"""

        namespace = self.create_task(image, **kwargs)

        obj = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self._sanitized_name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app.kubernetes.io/name": self._sanitized_name
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": int(port),
                    "targetPort": int(port)
                }]
            }
        }

        self.interfaces.k8s.add_object(obj)

        return f"{proto}://{self._sanitized_name}.{namespace}:{port}"


repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1Implementation
        ]
    }
}
