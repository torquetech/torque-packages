# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import components
from demo import providers
from demo import types


class Component(v1.component.Component):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {
            "host": str
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
    def on_requirements(cls) -> [v1.provider.Interface]:
        """TODO"""

        return {
            "lb": {
                "interface": providers.HttpLoadBalancers,
                "required": True
            }
        }

    def _host(self):
        """TODO"""

        return self.parameters["host"]

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.HttpLoadBalancer(host=self._host)
        ]

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        self.interfaces.lb.create(self.name)


class Link(v1.link.Link):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {
            "path": str
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
    def on_requirements(cls) -> object:
        """TODO"""

        return {
            "service": {
                "interface": components.HttpService,
                "bind_to": "source",
                "required": True
            },
            "lb": {
                "interface": components.HttpLoadBalancer,
                "bind_to": "destination",
                "required": True
            },
            "ingress": {
                "interface": providers.HttpIngressLinks,
                "bind_to": "source",
                "required": True
            }
        }

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        self.interfaces.ingress.create(self.source,
                                       self.interfaces.lb.host(),
                                       self.parameters["path"],
                                       types.NetworkLink(self.source,
                                                         self.interfaces.service.link()))
