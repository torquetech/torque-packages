# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import interface as interface_v1


class NetworkLink(interface_v1.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(component: str, address: int):
        """TODO"""


class VolumeLink(interface_v1.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(volume: str, mount_point: str):
        """TODO"""


class Service(interface_v1.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def get_address() -> (str, int):
        """TODO"""


class PythonModulesPath(interface_v1.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def get() -> str:
        """TODO"""


class PythonRequirements(interface_v1.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def add(requirements: [str]):
        """TODO"""


class SimpleDeployment(interface_v1.Interface):
    # pylint: disable=E0211,E0213

    """TODO"""

    def push_image(image: str):
        """TODO"""

    def create_task(name: str,
                    image: str,
                    network_links: [object],
                    volume_links: [object],
                    replicas: int):
        """TODO"""
