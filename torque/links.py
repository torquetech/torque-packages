# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import options

from torque.v1 import interfaces


class DependencyLink(interfaces.Link):
    """TODO"""

    @staticmethod
    def parameters() -> options.OptionsSpec:
        """TODO"""

        return options.OptionsSpec()

    @staticmethod
    def configuration() -> options.OptionsSpec:
        """TODO"""

        return options.OptionsSpec()

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self):
        """TODO"""
