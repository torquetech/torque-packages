# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import basics
from torque import docker_compose
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
                v1.schema.Optional(str): str
            }
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

        self._sanitized_name = self.name.replace(".", "-")

    def create_task(self, image: str, **kwargs):
        """TODO"""

        obj = {
            "image": image,
            "restart": "unless-stopped",
            "volumes": []
        }

        command = kwargs.get("command")
        arguments = kwargs.get("arguments")
        environment = kwargs.get("environment")
        working_directory = kwargs.get("working_directory")

        if command:
            obj["command"] = command

        else:
            if arguments:
                obj["command"] = arguments

        obj["environment"] = [
            f"{name.upper()}={value}" for name, value in environment
        ]

        obj["environment"].extend([
            f"{name.upper()}={value}" for name, value in self.configuration["environment"]
        ])

        for name, path in self.configuration["volumes"].items():
            volume_name = f"{self._sanitized_name}-{name}"

            self.interfaces.dc.add_object("volumes", volume_name, {})

            obj["volumes"].append({
                "type": "volume",
                "source": volume_name,
                "target": path
            })

        if working_directory:
            obj["working_dir"] = working_directory

        self.interfaces.dc.add_object("services", self._sanitized_name, obj)

    def create_service(self, image: str, proto: str, port: str, **kwargs) -> str:
        """TODO"""

        self.create_task(image, **kwargs)

        return f"{proto}://{self._sanitized_name}:{port}"


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
