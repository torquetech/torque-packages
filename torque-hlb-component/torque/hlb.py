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
    "path"
])


class V1LoadBalancerInterface(v1.bond.Interface):
    """TODO"""

    def create(self, ingress_list: [Ingress]):
        """TODO"""


class V1IngressInterface(v1.component.DestinationInterface):
    """TODO"""

    def add(self, ingress: Ingress):
        """TODO"""


class V1Component(v1.component.Component):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "hlb": {
                "interface": V1LoadBalancerInterface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ingress_list = []

    def _add_ingress(self, ingress: Ingress):
        """TODO"""

        self._ingress_list.append(ingress)

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            V1IngressInterface(add=self._add_ingress)
        ]

    def on_apply(self):
        """TODO"""

        self.interfaces.hlb.create(self._ingress_list)


repository = {
    "v1": {
        "components": [
            V1Component
        ]
    }
}
