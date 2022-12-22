# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from collections import namedtuple

from torque import docker_compose
from torque import v1


Entry = namedtuple("Entry", [
    "service",
    "domain",
    "hosts"
])


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "dc": {
                "interface": docker_compose.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._entries = []

    def add_entry(self, entry: Entry):
        """DOCSTRING"""

        self._entries.append(entry)

    def get_entries(self) -> [Entry]:
        """DOCSTRING"""

        return self._entries


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
