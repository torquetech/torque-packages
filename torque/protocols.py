# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import io

from torque import v1


class FileProtocol(v1.protocol.Protocol):
    """TODO"""

    @staticmethod
    def fetch(uri: str) -> io.TextIOWrapper:
        """TODO"""

        if uri.startswith("file://"):
            uri = uri[7:]

        else:
            uri = v1.utils.resolve_path(uri)

        return open(uri, encoding="utf8")
