# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class TorqueException(Exception):
    """TODO"""


class GroupNotEmpty(TorqueException):
    """TODO"""


class GroupNotFound(TorqueException):
    """TODO"""


class GroupExists(TorqueException):
    """TODO"""


class ComponentNotFound(TorqueException):
    """TODO"""


class ComponentExists(TorqueException):
    """TODO"""


class ComponentStillConnected(TorqueException):
    """TODO"""


class LinkNotFound(TorqueException):
    """TODO"""


class LinkExists(TorqueException):
    """TODO"""


class CycleDetected(TorqueException):
    """TODO"""


class ComponentsAlreadyConnected(TorqueException):
    """TODO"""

    def __init__(self, source: str, destination: str):
        super().__init__(f"{source}:{destination}")


class ComponentsNotConnected(TorqueException):
    """TODO"""

    def __init__(self, source: str, destination: str):
        super().__init__(f"{source}:{destination}")


class ComponentTypeNotFound(TorqueException):
    """TODO"""


class LinkTypeNotFound(TorqueException):
    """TODO"""


class PackageNotFound(TorqueException):
    """TODO"""


class PackageInUse(TorqueException):
    """TODO"""


class ExecuteFailed(TorqueException):
    """TODO"""


class OptionRequired(TorqueException):
    """TODO"""


class ProtocolNotFound(TorqueException):
    """TODO"""


class ProfileExists(TorqueException):
    """TODO"""


class ProfileNotFound(TorqueException):
    """TODO"""
