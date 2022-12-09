# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

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
    """TODO"""

    def add(self, ingress: Ingress):
        """TODO"""


class V1DestinationInterface(v1.component.DestinationInterface):
    """TODO"""

    def add(self, ingress: Ingress):
        """TODO"""


class V1Component(v1.component.Component):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "impl": {
                "interface": V1ImplementationInterface,
                "required": True
            }
        }

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

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
