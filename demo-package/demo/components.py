# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import utils


class Service(v1.component.SourceInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def link() -> utils.Future[object]:
        """TODO"""


class HttpService(v1.component.SourceInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def link() -> utils.Future[object]:
        """TODO"""


class PostgresService(v1.component.SourceInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def link() -> utils.Future[object]:
        """TODO"""

    def admin() -> utils.Future[object]:
        """TODO"""


class Postgres(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def data_path() -> str:
        """TODO"""


class ZookeeperService(v1.component.SourceInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def link() -> utils.Future[object]:
        """TODO"""


class Zookeeper(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def data_path() -> str:
        """TODO"""


class KafkaService(v1.component.SourceInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def link() -> utils.Future[object]:
        """TODO"""


class Kafka(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def data_path() -> str:
        """TODO"""

    def zookeeper(link: utils.Future[object]):
        """TODO"""


class NetworkLink(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(name: str, link: utils.Future[object]):
        """TODO"""


class Volume(v1.component.SourceInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def link() -> utils.Future[object]:
        """TODO"""


class VolumeLink(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(name: str, mount_path: str, link: utils.Future[object]):
        """TODO"""


class SecretLink(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(name: str, key: str, link: utils.Future[object]):
        """TODO"""


class Environment(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(name: str, value: str):
        """TODO"""


class PythonModules(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def path() -> str:
        """TODO"""

    def add_requirements(requirements: [str]):
        """TODO"""


class HttpLoadBalancer(v1.component.DestinationInterface):
    # pylint: disable=E0211,E0213

    """TODO"""
