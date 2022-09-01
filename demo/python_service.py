# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import components
from demo import providers
from demo import python_app


class Component(python_app.Component):
    """TODO"""

    # pylint: disable=W0212
    _CONFIGURATION = v1.utils.merge_dicts(python_app.Component._CONFIGURATION, {
        "defaults": {
            "port": 8080
        },
        "schema": {
            "port": int
        }
    }, allow_overwrites=False)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return super().on_requirements() | {
            "services": {
                "interface": providers.Services,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._service_link = None

    def _link(self) -> v1.utils.Future[object]:
        """TODO"""

        return self._service_link

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return super().on_interfaces() + [
            components.HttpService(link=self._link)
        ]

    def on_apply(self, context: v1.deployment.Context):
        """TODO"""

        self._service_link = self.bonds.services.create(self.name,
                                                        "tcp",
                                                        self.configuration["port"],
                                                        self.configuration["port"])

        super().on_apply(context)
