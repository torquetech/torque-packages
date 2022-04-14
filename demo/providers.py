# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import schema

from torque import v1

from demo import interfaces


class AWSK8S(v1.provider.Provider):
    """TODO"""

    _DEFAULT_CONFIGURATION = {}
    _CONFIGURATION_SCHEMA = schema.Schema({})

    @staticmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

        configuration = v1.utils.merge_dicts(AWSK8S._DEFAULT_CONFIGURATION, configuration)

        try:
            return AWSK8S._CONFIGURATION_SCHEMA.validate(configuration)

        except schema.SchemaError as exc:
            raise RuntimeError(f"invalid configuration") from exc

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

    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return [
            interfaces.SimpleDeployment(push_image=self._push_image,
                                        create_task=self._create_task)
        ]
