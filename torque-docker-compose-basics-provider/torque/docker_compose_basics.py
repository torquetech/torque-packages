# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import basics
from torque import docker_compose
from torque import v1


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1TaskImplementation(v1.bond.Bond):
    """TODO"""

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
        """TODO"""

        return {
            "dc": {
                "interface": docker_compose.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._environment = []
        self._image = None
        self._command = None
        self._arguments = None
        self._working_directory = None

        with self.interfaces.dc as p:
            p.add_hook("apply-objects", self._apply)

    def _apply(self):
        """TODO"""

        obj = {
            "image": self._image,
            "restart": "unless-stopped"
        }

        if self._command:
            obj["command"] = self._command

        else:
            if self._arguments:
                obj["command"] = self._arguments

        obj["environment"] = {
            name.upper(): value
            for name, value in self.configuration["environment"].items()
        }

        obj["environment"].update({
            name.upper(): v1.utils.resolve_futures(value)
            for name, value in self._environment
        })

        path = self.configuration.get("volume")

        if path:
            self.interfaces.dc.add_object("volumes", self.name, {})

            obj["volumes"] = [{
                "type": "volume",
                "source": self.name,
                "target": path
            }]

        if self._working_directory:
            obj["working_dir"] = self._working_directory

        self.interfaces.dc.add_object("services", self.name, obj)

    def add_environment(self, name: str, value: v1.utils.Future[str] | str):
        """TODO"""

        self._environment.append((name, value))

    def set_image(self, image: str):
        """TODO"""

        self._image = image

    def set_command(self, command: [str]):
        """TODO"""

        self._command = command

    def set_arguments(self, arguments: [str]):
        """TODO"""

        self._arguments = arguments

    def set_working_directory(self, working_directory: str):
        """TODO"""

        self._working_directory = working_directory


class V1ServiceImplementation(V1TaskImplementation):
    """TODO"""

    IMPLEMENTS = basics.V1ServiceImplementationInterface

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._proto = None
        self._port = None

    def set_proto(self, proto: str):
        """TODO"""

        self._proto = proto

    def set_port(self, port: int):
        """TODO"""

        self._port = port

    def service(self) -> basics.Service:
        """TODO"""

        return basics.Service(self._proto, self.name, self._port)


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
