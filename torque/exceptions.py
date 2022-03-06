# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class TorqueException(Exception):
    """TODO"""


class ClusterNotEmpty(TorqueException):
    """TODO"""


class ClusterNotFound(TorqueException):
    """TODO"""


class DuplicateCluster(TorqueException):
    """TODO"""


class ComponentNotFound(TorqueException):
    """TODO"""


class DuplicateComponent(TorqueException):
    """TODO"""


class ComponentStillConnected(TorqueException):
    """TODO"""


class DuplicateLink(TorqueException):
    """TODO"""


class CycleDetected(TorqueException):
    """TODO"""


class LinkNotFound(TorqueException):
    """TODO"""


class LinkAlreadyExists(TorqueException):
    """TODO"""

    def __init__(self, source: str, destination: str):
        super().__init__(f"{source}:{destination}")
