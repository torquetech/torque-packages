# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple

from torque import v1


Authorization = namedtuple("Authorization", [
    "database",
    "user",
    "password"
])

Service = namedtuple("Service", [
    "host",
    "port",
    "options"
])


class V1ImplementationInterface(v1.bond.Interface):
    """TODO"""

    def auth(self, database: str, user: str) -> v1.utils.Future[Authorization]:
        """TODO"""

    def service(self) -> v1.utils.Future[Service] | Service:
        """TODO"""


class V1SourceInterface(v1.component.SourceInterface):
    """TODO"""

    def auth(self, database: str, user: str) -> v1.utils.Future[Authorization]:
        """TODO"""

    def service(self) -> v1.utils.Future[Service] | Service:
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
            V1SourceInterface(auth=self.interfaces.impl.auth,
                              service=self.interfaces.impl.service)
        ]


repository = {
    "v1": {
        "components": [
            V1Component
        ]
    }
}
