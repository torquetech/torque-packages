# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import collections

from torque import v1


Ingress = collections.namedtuple("Ingress", [
    "id",
    "service",
    "port",
    "host",
    "path",
    "options"
])


class V1ImplementationInterface(v1.bond.Interface):
    """DOCSTRING"""

    def add(self, ingress: v1.utils.Future[Ingress]):
        """DOCSTRING"""


class V1DestinationInterface(v1.component.DestinationInterface):
    """DOCSTRING"""

    def add(self, ingress: v1.utils.Future[Ingress]):
        """DOCSTRING"""


class V1Component(v1.component.Component):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "impl": {
                "interface": V1ImplementationInterface,
                "required": True
            }
        }

    def on_interfaces(self) -> [v1.component.Interface]:
        """DOCSTRING"""

        return [
            V1DestinationInterface(add=self.interfaces.impl.add)
        ]


repository = {
    "v1": {
        "components": [
            V1Component
        ]
    }
}
