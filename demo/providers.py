# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import abstractmethod
from collections import namedtuple

from torque import v1


KeyValue = namedtuple("KeyValue", [
    "key",
    "value"
])

NetworkLink = namedtuple("NetworkLink", [
    "name",
    "object"
])

VolumeLink = namedtuple("VolumeLink", [
    "name",
    "mount_path",
    "object"
])

SecretLink = namedtuple("SecretLink", [
    "name",
    "key",
    "object"
])


class ImagesProvider(v1.provider.Provider):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def push(self, image: str):
        """TODO"""


class SecretsProvider(v1.provider.Provider):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str, entries: [KeyValue]) -> v1.utils.Future[object]:
        """TODO"""


class ServicesProvider(v1.provider.Provider):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str, tcp_ports: [int], udp_ports: [int]) -> v1.utils.Future[object]:
        """TODO"""


class DeploymentsProvider(v1.provider.Provider):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self,
               name: str,
               image: str,
               cmd: [str],
               args: [str],
               cwd: str,
               env: [KeyValue],
               network_links: [NetworkLink],
               volume_links: [VolumeLink],
               secret_links: [SecretLink],
               replicas: int):
        """TODO"""
