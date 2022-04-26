# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import interfaces


class Link(v1.link.Link):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
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
                interfaces.Service,
                "source",
                "src",
                True
            ),
            v1.utils.InterfaceRequirement(
                interfaces.NetworkLink,
                "destination",
                "dst",
                True
            )
        ]

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        self.interfaces.dst.add(self.source, self.interfaces.src.link())
