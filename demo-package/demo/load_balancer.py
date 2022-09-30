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

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "lb": {
                "interface": providers.HttpLoadBalancers,
                "required": True
            }
        }

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.HttpLoadBalancer()
        ]

    def on_apply(self):
        """TODO"""

        self.interfaces.lb.create()


class Link(v1.link.Link):
    """TODO"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            "path": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "service": {
                "interface": components.HttpService,
                "required": True
            },
            "lb": {
                "interface": components.HttpLoadBalancer,
                "required": True
            },
            "ingress": {
                "interface": providers.HttpIngressLinks,
                "required": True
            }
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.ingress.create(self.source,
                                       self.parameters["path"],
                                       types.NetworkLink(self.source,
                                                         self.interfaces.service.link()))
