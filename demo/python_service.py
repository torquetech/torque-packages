# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import interfaces
from demo import utils

from demo.python_task import Task

class Service(Task):
    """TODO"""

    _CONFIGURATION = v1.utils.merge_dicts(Task._CONFIGURATION, {
        "defaults": {
            "tcp_ports": [],
            "udp_ports": []
        },
        "schema": {
            "tcp_ports": [int],
            "udp_ports": [int]
        }
    }, allow_overwrites=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._service_link = None

    def _link(self) -> (str, int):
        # pylint: disable=R0201

        """TODO"""

        return self._service_link

    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return super().interfaces() + [
            interfaces.Service(link=self._link)
        ]

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        provider = deployment.interface(interfaces.Provider)

        self._service_link = provider.create_service(self.name,
                                                     self.configuration["tcp_ports"],
                                                     self.configuration["udp_ports"])

        Task.on_apply(self, deployment)

        return True
