# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class TorqueException(Exception):
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


class ComponentsNotConnected(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]},{self.args[1]}"


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


class ConfigurationRequired(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: {self.args[1]}: {self.args[2]}"


class ProtocolNotFound(TorqueException):
    """TODO"""


class ProfileExists(TorqueException):
    """TODO"""


class ProfileNotFound(TorqueException):
    """TODO"""


class ProviderNotFound(TorqueException):
    """TODO"""


class InvalidName(TorqueException):
    """TODO"""


class DeploymentExists(TorqueException):
    """TODO"""


class DeploymentNotFound(TorqueException):
    """TODO"""


class NoComponentsSelected(TorqueException):
    """TODO"""
