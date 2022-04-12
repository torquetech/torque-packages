# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import component as component_v1

from demo import interfaces
from demo import python_task


class PythonService(python_task.PythonTask):
    """TODO"""

    def _get_network_address(self) -> (str, int):
        # pylint: disable=R0201

        """TODO"""

        return ("", 0)

    def outbound_interfaces(self) -> [component_v1.Interface]:
        """TODO"""

        return super().outbound_interfaces() + [
            interfaces.Service(get_address=self._get_network_address)
        ]

    def on_generate(self, deployment: str, profile: str) -> bool:
        """TODO"""

        return True
