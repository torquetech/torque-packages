# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple

from torque import k8s
from torque import v1


Entry = namedtuple("Entry", [
    "service",
    "domain",
    "hosts"
])


class V1Provider(v1.provider.Provider):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "dc": {
                "interface": k8s.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._entries = []

    def add_entry(self, entry: Entry):
        """TODO"""

        self._entries.append(entry)

    def get_entries(self) -> [Entry]:
        """TODO"""

        return self._entries


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
