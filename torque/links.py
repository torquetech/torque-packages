# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1


class DependencyLink(v1.link.Link):
    """TODO"""

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        return {}

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return {}

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        return {}

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""
