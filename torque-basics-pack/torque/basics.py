# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess

from urllib.parse import urlparse

from torque import hlb
from torque import postgres
from torque import v1


class V1ImplementationInterface(v1.bond.Interface):
    """TODO"""

    def create_task(self, image: str, **kwargs):
        """TODO"""

    def create_service(self, image: str, proto: str, port: str, **kwargs) -> str:
        """TODO"""


class V1TCPServiceInterface(v1.component.SourceInterface):
    """TODO"""

    def uri(self) -> str:
        """TODO"""


class V1HttpServiceInterface(v1.component.SourceInterface):
    """TODO"""

    def uri(self) -> str:
        """TODO"""


class V1EnvironmentInterface(v1.component.DestinationInterface):
    """TODO"""

    def add(self, name: str, value: str):
        """TODO"""


class BaseComponent(v1.component.Component):
    """TODO"""

    PARAMETERS = {
        "defaults": {
            "build": {
                "command": [
                    "docker", "build",
                    "-t", "$IMAGE", "."
                ]
            },
            "run": {},
            "environment": {}
        },
        "schema": {
            "path": str,
            "build": {
                "command": [str]
            },
            "run": {
                v1.schema.Optional("command"): [str],
                v1.schema.Optional("arguments"): [str],
                v1.schema.Optional("work_directory"): str
            },
            "environment": {
                v1.schema.Optional(str): str
            }
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "impl": {
                "interface": V1ImplementationInterface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._path = v1.utils.resolve_path(self.parameters["path"])
        self._image = None

        self._environment = [
            (name, value) for name, value in self.parameters["environment"].items()
        ]

    def _add_environment(self, name: str, value: str):
        """TODO"""

        self._environment.append((name, value))

    def _get_image(self) -> str:
        """TODO"""

        if self._image:
            return self._image

        self._image = f"{self.name}:latest"

        return self._image

    def _resolve_cmd(self) -> [str]:
        """TODO"""

        cmd = []

        for i in self.parameters["build"]["command"]:
            i = i.replace("$IMAGE", self._get_image())
            cmd.append(i)

        return cmd

    def on_interfaces(self):
        """TODO"""

        return [
            V1EnvironmentInterface(add=self._add_environment)
        ]

    def on_build(self):
        """TODO"""

        cmd = self._resolve_cmd()

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self._path, check=True)


class BaseService(BaseComponent):
    """TODO"""

    PARAMETERS = v1.utils.merge_dicts(BaseComponent.PARAMETERS, {
        "defaults": {},
        "schema": {
            "port": str
        }
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = None
        self._uri = None

    def _get_uri(self) -> v1.utils.Future[str]:
        """TODO"""

        return self._uri

    def on_apply(self):
        """TODO"""

        self._uri = self.interfaces.impl.create_service(self._get_image(),
                                                        self._proto,
                                                        self.parameters["port"],
                                                        environment=self._environment,
                                                        commands=self.parameters.get("command"),
                                                        arguments=self.parameters.get("arguments"),
                                                        working_directory=self.parameters.get("working_directory"))


class V1Task(BaseComponent):
    """TODO"""

    def on_apply(self):
        """TODO"""

        self.interfaces.impl.create_task(self._get_image(),
                                         environment=self._environment,
                                         commands=self.parameters.get("command"),
                                         arguments=self.parameters.get("arguments"),
                                         working_directory=self.parameters.get("working_directory"))


class V1TCPService(BaseService):
    """TODO"""

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

    def on_interfaces(self):
        """TODO"""

        return super().on_interfaces() + [
            V1TCPServiceInterface(uri=self._get_uri)
        ]


class V1HttpService(BaseService):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = "http"

    def on_interfaces(self):
        """TODO"""

        return super().on_interfaces() + [
            V1HttpServiceInterface(uri=self._get_uri)
        ]


class V1IngressLink(v1.link.Link):
    """TODO"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            "host": str,
            "path": str
        }
    }

    @classmethod
    def on_requirements(cls):
        """TODO"""

        return {
            "src": {
                "interface": V1HttpServiceInterface,
                "required": True
            },
            "dst": {
                "interface": hlb.V1IngressInterface,
                "required": True
            }
        }

    def on_apply(self):
        """TODO"""

        uri = urlparse(self.interfaces.src.uri())

        self.interfaces.dst.add(hlb.Ingress(self.name,
                                            uri.hostname,
                                            uri.port,
                                            self.parameters["host"],
                                            self.parameters["path"]))


class BaseLink(v1.link.Link):
    """TODO"""

    @classmethod
    def on_requirements(cls):
        """TODO"""

        return {
            "dst": {
                "interface": V1EnvironmentInterface,
                "required": True
            }
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.dst.add(self.source.replace(".", "_"),
                                self.interfaces.src.uri())


class V1PostgresLink(BaseLink):
    """TODO"""

    PARAMETERS = v1.utils.merge_dicts(BaseLink.PARAMETERS, {
        "defaults": {},
        "schema": {
            "database": str,
            "user": str
        }
    })

    @classmethod
    def on_requirements(cls):
        """TODO"""

        return super().on_requirements() | {
            "src": {
                "interface": postgres.V1ServiceInterface,
                "required": True
            }
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.dst.add(self.source.replace(".", "_"),
                                self.interfaces.src.uri(self.parameters["database"],
                                                        self.parameters["user"]))


class V1TCPServiceLink(BaseLink):
    """TODO"""

    @classmethod
    def on_requirements(cls):
        """TODO"""

        return super().on_requirements() | {
            "src": {
                "interface": V1TCPServiceInterface,
                "required": True
            }
        }


class V1HttpServiceLink(BaseLink):
    """TODO"""

    @classmethod
    def on_requirements(cls):
        """TODO"""

        return super().on_requirements() | {
            "src": {
                "interface": V1HttpServiceInterface,
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
            V1PostgresLink,
            V1TCPServiceLink,
            V1HttpServiceLink
        ]
    }
}
