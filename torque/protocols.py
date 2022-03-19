# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import io

from torque.v1 import interfaces


class FileProtocol(interfaces.Protocol):
    # pylint: disable=R0903

    """TODO"""

    @staticmethod
    def fetch(uri: str, secret: str) -> io.TextIOWrapper:
        """TODO"""
        return open(uri, encoding="utf8")
