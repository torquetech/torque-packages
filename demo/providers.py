# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import abstractmethod

from torque import v1

from demo import types


class Images(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def push(self, image: str):
        """TODO"""


class Secrets(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str, entries: [types.KeyValue]) -> v1.utils.Future[object]:
        """TODO"""


class Services(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str, type: str, port: int, target_port: int) -> v1.utils.Future[object]:
        """TODO"""


class Deployments(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self,
               name: str,
               image: str,
               cmd: [str],
               args: [str],
               cwd: str,
               env: [types.KeyValue],
               ports: [types.Port],
               network_links: [types.NetworkLink],
               volume_links: [types.VolumeLink],
               secret_links: [types.SecretLink],
               replicas: int):
        """TODO"""


class PersistentVolumes(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str, volume_id: str) -> v1.utils.Future[object]:
        """TODO"""


class HttpLoadBalancers(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str):
        """TODO"""


class PersistentVolumesProvider(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self, name: str, size: int) -> v1.utils.Future[object]:
        """TODO"""


class HttpIngressLinks(v1.provider.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    @abstractmethod
    def create(self,
               name: str,
               host: str,
               path: str,
               network_link: types.NetworkLink):
        """TODO"""
