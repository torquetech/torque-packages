# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from torque import v1


class V1DestinationInterface(v1.component.DestinationInterface):
    """DOCSTRING"""

    def add(self, name: str, value: v1.utils.Future[str] | str):
        """DOCSTRING"""


class V1BaseLink(v1.link.Link):
    """DOCSTRING"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            v1.schema.Optional("name"): str
        }
    }

    @classmethod
    def on_requirements(cls):
        """DOCSTRING"""

        return {
            "dst": {
                "interface": V1DestinationInterface,
                "required": True
            }
        }

    def _name(self) -> str:
        """DOCSTRING"""

        name = self.parameters.get("name", self.source)
        name = name.replace("-", "_")
        name = name.upper()

        return name
