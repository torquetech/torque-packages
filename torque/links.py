# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import dsl as dsl_v1
from torque.v1 import link as link_v1
from torque.v1 import options as options_v1


class DependencyLink(link_v1.Link):
    """TODO"""

    @staticmethod
    def parameters() -> options_v1.OptionsSpec:
        """TODO"""

        return options_v1.OptionsSpec()

    @staticmethod
    def configuration() -> options_v1.OptionsSpec:
        """TODO"""

        return options_v1.OptionsSpec()

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, source_artifacts: list[str]) -> list[str]:
        """TODO"""

        return []

    def on_generate(self) -> list[dsl_v1.Instruction]:
        """TODO"""

        return []
