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

    def on_create(self):
        """TODO"""

        if not self.source.has_interface(interfaces.Service):
            raise RuntimeError(f"{self.source.name}: incompatible component")

        if not self.destination.has_interface(interfaces.NetworkLink):
            raise RuntimeError(f"{self.destination.name}: incompatible component")

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        src = self.source.interface(interfaces.Service)
        dst = self.destination.interface(interfaces.NetworkLink)

        dst.add(self.source.name, src.link())
