# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import interfaces
from demo import volume


class Link(volume.Link):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_requirements(cls) -> [v1.provider.Interface]:
        """TODO"""

        return super().on_requirements() + [
            v1.utils.InterfaceRequirement(
                interfaces.PostgresService,
                "destination",
                "pg",
                True
            ),
        ]

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        self.interfaces.dst.add(self.source,
                                self.interfaces.pg.pg_data(),
                                self.interfaces.src.link())
