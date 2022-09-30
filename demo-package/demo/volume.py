# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import components


class Link(v1.link.Link):
    """TODO"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            "mount_point": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "src": {
                "interface": components.Volume,
                "required": True
            },
            "dst": {
                "interface": components.VolumeLink,
                "required": True
            },
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.dst.add(self.source,
                                self.parameters["mount_point"],
                                self.interfaces.src.link())
