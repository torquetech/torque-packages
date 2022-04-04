# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

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

    def on_build(self) -> bool:
        """TODO"""

        return True

    def on_generate(self) -> bool:
        """TODO"""

        return True
