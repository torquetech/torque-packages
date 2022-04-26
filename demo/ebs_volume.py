# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import interfaces


def _validate_size(size: object) -> int:
    """TODO"""

    if size is None:
        raise ValueError()

    size = int(size)

    if size < 1 or size > 128:
        raise ValueError()

    return size


class Component(v1.component.Component):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {
            "size": v1.schema.Use(_validate_size)
        }
    }

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._PARAMETERS["schema"],
                                        cls._PARAMETERS["defaults"],
                                        parameters)

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> [v1.utils.InterfaceRequirement]:
        """TODO"""

        return [
            v1.utils.InterfaceRequirement(
                interfaces.EBSProvider,
                "provider",
                "t_ebs",
                True
            ),
            v1.utils.InterfaceRequirement(
                interfaces.EBSVolumes,
                "provider",
                "k_ebs",
                True
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._volume_link = None

    def _link(self) -> v1.utils.Future[object]:
        """TODO"""

        return self._volume_link

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            interfaces.Volume(link=self._link)
        ]

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        volume_id = self.interfaces.t_ebs.create(self.name, self.parameters["size"])
        self._volume_link = self.interfaces.k_ebs.create(self.name, volume_id.get())
