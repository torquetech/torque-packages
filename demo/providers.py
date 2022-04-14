# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import schema

from torque import v1

from demo import interfaces
from demo import utils


_DEFAULT_CONFIGURATION = {}
_CONFIGURATION_SCHEMA = schema.Schema({})


class AWSK8S(v1.provider.Provider):
    """TODO"""

    @staticmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

        return utils.validate_schema("configuration",
                                     configuration,
                                     _DEFAULT_CONFIGURATION,
                                     _CONFIGURATION_SCHEMA)

    def _push_image(self, image: str):
        """TODO"""

        print(f"_push_image({image}) called")

    def _create_task(self,
                     name: str,
                     image: str,
                     cmd: [str],
                     cwd: str,
                     env: dict[str, str],
                     network_links: [object],
                     volume_links: [object],
                     replicas: int):
        """TODO"""

        print(f"_create_task({name}, {image}) called")

    def _create_service(self,
                        name: str,
                        image: str,
                        cmd: [str],
                        cwd: str,
                        env: dict[str, str],
                        network_links: [object],
                        volume_links: [object],
                        tcp_ports: [int],
                        udp_ports: [int],
                        replicas: int) -> v1.interface.Future:
        """TODO"""

        print(f"_create_service({name}, {image}) called")

    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return [
            interfaces.SimpleDeployment(push_image=self._push_image,
                                        create_task=self._create_task,
                                        create_service=self._create_service)
        ]
