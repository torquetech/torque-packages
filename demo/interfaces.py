# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1


class Service(v1.interface.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def get() -> v1.interface.Future:
        """TODO"""


class NetworkLink(v1.interface.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(link: v1.interface.Future):
        """TODO"""


class Volume(v1.interface.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def get(size: int) -> v1.interface.Future:
        """TODO"""

class VolumeLink(v1.interface.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(mount_point: str, link: v1.interface.Future):
        """TODO"""


class PythonModules(v1.interface.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def path() -> str:
        """TODO"""

    def add_requirements(requirements: [str]):
        """TODO"""


class SimpleDeployment(v1.interface.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def push_image(image: str):
        """TODO"""

    def create_task(name: str,
                    image: str,
                    cmd: [str],
                    cwd: str,
                    env: dict[str, str],
                    network_links: [object],
                    volume_links: [object],
                    replicas: int):
        """TODO"""

    def create_service(name: str,
                       image: str,
                       cmd: [str],
                       cwd: str,
                       env: dict[str, str],
                       network_links: [object],
                       volume_links: [object],
                       tcp_ports: [int],
                       udp_ports: [int],
                       replicas: int) -> v1.interface.Future:
        """TODO"""
