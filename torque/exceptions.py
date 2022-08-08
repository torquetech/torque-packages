# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class TorqueException(Exception):
    """TODO"""


class ComponentNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: component not found"


class ComponentExists(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: component already exists"


class ComponentStillConnected(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: component still connected"


class LinkNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: link not found"


class LinkExists(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: link already exists"


class CycleDetected(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"cycle detected, can't continue"


class ComponentsNotConnected(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]},{self.args[1]}: components not connected"


class ComponentTypeNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: component type not found"


class LinkTypeNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: link type not found"


class PackageNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: package not found"


class ProtocolNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: protocol not found"


class ProfileExists(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: profile already exists"


class ProfileNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: profile not found"


class ProviderNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: provider not found"


class InterfaceNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: interface not found"


class BindNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: bind not found"


class InvalidBind(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: invalid bind"


class InvalidRequirement(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: invalid requirements"


class InvalidName(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: invalid name"


class DeploymentExists(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: deployment already exists"


class DeploymentNotFound(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: deployment not found"


class NoComponentsSelected(TorqueException):
    """TODO"""

    def __str__(self) -> str:
        return f"{self.args[0]}: no components selected"


class OperationAborted(TorqueException):
    """TODO"""
