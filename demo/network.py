# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import components


class Link(v1.link.Link):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "src": {
                "interface": components.Service,
                "required": True
            },
            "dst": {
                "interface": components.NetworkLink,
                "required": True
            }
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.dst.add(self.source,
                                self.interfaces.src.link())
