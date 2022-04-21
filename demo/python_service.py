# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import interfaces
from demo import python_app


class Component(python_app.Component):
    """TODO"""

    # pylint: disable=W0212
    _CONFIGURATION = v1.utils.merge_dicts(python_app.Component._CONFIGURATION, {
        "defaults": {
            "tcp_ports": [],
            "udp_ports": []
        },
        "schema": {
            "tcp_ports": [int],
            "udp_ports": [int]
        }
    }, allow_overwrites=False)

    @classmethod
    def on_requirements(cls) -> [v1.provider.Interface]:
        """TODO"""

        return super().on_requirements() + [
            v1.utils.InterfaceRequirement(interfaces.ServicesInterface, "provider", "services")
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._service_link = None

    def _link(self) -> v1.utils.Future[object]:
        """TODO"""

        return self._service_link

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return super().on_interfaces() + [
            interfaces.Service(link=self._link)
        ]

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        self._service_link = self.interfaces.services.create(self.name,
                                                             self.configuration["tcp_ports"],
                                                             self.configuration["udp_ports"])

        super().on_apply(deployment)
