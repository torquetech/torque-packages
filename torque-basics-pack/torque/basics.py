# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os
import subprocess

from collections import namedtuple

from torque import environment
from torque import hlb
from torque import v1


Service = namedtuple("Service", [
    "proto",
    "host",
    "port"
])


class V1TaskImplementationInterface(v1.bond.Interface):
    """DOCSTRING"""

    def add_environment(self, name: str, value: v1.utils.Future[str] | str):
        """DOCSTRING"""

    def set_image(self, tag: str, id: str):
        """DOCSTRING"""

    def set_command(self, command: [str]):
        """DOCSTRING"""

    def set_arguments(self, arguments: [str]):
        """DOCSTRING"""

    def set_working_directory(self, working_directory: str):
        """DOCSTRING"""


class V1ServiceImplementationInterface(v1.bond.Interface):
    """DOCSTRING"""

    def add_environment(self, name: str, value: v1.utils.Future[str] | str):
        """DOCSTRING"""

    def set_image(self, tag: str, id: str):
        """DOCSTRING"""

    def set_command(self, command: [str]):
        """DOCSTRING"""

    def set_arguments(self, arguments: [str]):
        """DOCSTRING"""

    def set_working_directory(self, working_directory: str):
        """DOCSTRING"""

    def set_proto(self, proto: str):
        """DOCSTRING"""

    def set_port(self, port: int):
        """DOCSTRING"""

    def service(self) -> v1.utils.Future[Service]:
        """DOCSTRING"""


class V1TCPSourceInterface(v1.component.SourceInterface):
    """DOCSTRING"""

    def service(self) -> v1.utils.Future[Service]:
        """DOCSTRING"""


class V1HttpSourceInterface(v1.component.SourceInterface):
    """DOCSTRING"""

    def service(self) -> v1.utils.Future[Service]:
        """DOCSTRING"""


class BaseComponent(v1.component.Component):
    """DOCSTRING"""

    PARAMETERS = {
        "defaults": {
            "build": {
                "command": [
                    "docker", "build",
                    "-t", "$IMAGE", "."
                ]
            },
            "run": {}
        },
        "schema": {
            "path": str,
            "build": {
                "command": [str]
            },
            "run": {
                v1.schema.Optional("command"): [str],
                v1.schema.Optional("arguments"): [str],
                v1.schema.Optional("working_directory"): str
            }
        }
    }

    def _resolve_cmd(self, image: str) -> [str]:
        """DOCSTRING"""

        cmd = []

        for i in self.parameters["build"]["command"]:
            i = i.replace("$IMAGE", image)
            cmd.append(i)

        return cmd

    def _id(self, image: str) -> str:
        """DOCSTRING"""

        cmd = [
            "docker", "image", "inspect",
            "-f", "{{.Id}}",
            image
        ]

        print(f"+ {' '.join(cmd)}")

        p = subprocess.run(cmd,
                           env=os.environ,
                           check=True,
                           capture_output=True)

        return p.stdout.decode("utf8").strip()

    def on_interfaces(self) -> [v1.component.Interface]:
        """DOCSTRING"""

        return [
            environment.V1DestinationInterface(add=self.interfaces.impl.add_environment)
        ]

    def on_build(self):
        """DOCSTRING"""

        image = f"{self.context.deployment_name}-{self.name}:latest"

        path = v1.utils.resolve_path(self.parameters["path"])
        cmd = self._resolve_cmd(image)

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       cwd=path,
                       check=True)

        image = {
            "tag": image,
            "id": self._id(image)
        }

        with self.context as ctx:
            ctx.set_data("images", self.name, image)

    def on_apply(self):
        """DOCSTRING"""

        with self.context as ctx:
            image = ctx.get_data("images", self.name)

        if not image:
            raise v1.exceptions.RuntimeError(f"{self.name}: image not found")

        self.interfaces.impl.set_image(image["tag"], image["id"])
        self.interfaces.impl.set_command(self.parameters["run"].get("command"))
        self.interfaces.impl.set_arguments(self.parameters["run"].get("arguments"))
        self.interfaces.impl.set_working_directory(self.parameters["run"].get("working_directory"))


class V1Task(BaseComponent):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "impl": {
                "interface": V1TaskImplementationInterface,
                "required": True
            }
        }


class BaseService(BaseComponent):
    """DOCSTRING"""

    PARAMETERS = v1.utils.merge_dicts(BaseComponent.PARAMETERS, {
        "defaults": {},
        "schema": {
            "port": str
        }
    })

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "impl": {
                "interface": V1ServiceImplementationInterface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = None

    def on_apply(self):
        """DOCSTRING"""

        super().on_apply()

        self.interfaces.impl.set_proto(self._proto)
        self.interfaces.impl.set_port(int(self.parameters["port"]))


class V1TCPService(BaseService):
    """DOCSTRING"""

    PARAMETERS = v1.utils.merge_dicts(BaseService.PARAMETERS, {
        "defaults": {
            "proto": "tcp"
        },
        "schema": {
            "proto": str
        }
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = self.parameters["proto"]

    def on_interfaces(self) -> [v1.component.Interface]:
        """DOCSTRING"""

        return super().on_interfaces() + [
            V1TCPSourceInterface(service=self.interfaces.impl.service)
        ]


class V1HttpService(BaseService):
    """DOCSTRING"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = "http"

    def on_interfaces(self) -> [v1.component.Interface]:
        """DOCSTRING"""

        return super().on_interfaces() + [
            V1HttpSourceInterface(service=self.interfaces.impl.service)
        ]


class V1IngressLink(v1.link.Link):
    """DOCSTRING"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            "host": str,
            "path": str
        }
    }

    @classmethod
    def on_requirements(cls):
        """DOCSTRING"""

        return {
            "src": {
                "interface": V1HttpSourceInterface,
                "required": True
            },
            "dst": {
                "interface": hlb.V1DestinationInterface,
                "required": True
            }
        }

    def _resolve_ingress(self, service: v1.utils.Future[Service]) -> str:
        """DOCSTRING"""

        service = v1.utils.resolve_futures(service)

        return hlb.Ingress(self.name,
                           service.host,
                           service.port,
                           self.parameters["host"],
                           self.parameters["path"],
                           {})

    def on_apply(self):
        """DOCSTRING"""

        self.interfaces.dst.add(v1.utils.Future(self._resolve_ingress, self.interfaces.src.service()))


class BaseLink(environment.V1BaseLink):
    """DOCSTRING"""

    def _resolve_uri(self, service: v1.utils.Future[Service]):
        """DOCSTRING"""

        service = v1.utils.resolve_futures(service)

        return f"{service.proto}://{service.host}:{service.port}"

    def on_apply(self):
        """DOCSTRING"""

        service = self.interfaces.src.service()

        self.interfaces.dst.add(self._name(), v1.utils.Future(self._resolve_uri, service))


class V1TCPServiceLink(BaseLink):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls):
        """DOCSTRING"""

        return super().on_requirements() | {
            "src": {
                "interface": V1TCPSourceInterface,
                "required": True
            }
        }


class V1HttpServiceLink(BaseLink):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls):
        """DOCSTRING"""

        return super().on_requirements() | {
            "src": {
                "interface": V1HttpSourceInterface,
                "required": True
            }
        }


repository = {
    "v1": {
        "components": [
            V1Task,
            V1TCPService,
            V1HttpService
        ],
        "links": [
            V1IngressLink,
            V1TCPServiceLink,
            V1HttpServiceLink
        ]
    }
}
