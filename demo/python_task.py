# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import component as component_v1
from torque.v1 import options as options_v1

from demo import interfaces
from demo import tao


class PythonTask(component_v1.Component):
    """TODO"""

    @staticmethod
    def parameters() -> [options_v1.OptionSpec]:
        """TODO"""

        return [
            options_v1.OptionSpec("path", "component's path", None, str)
        ]

    @staticmethod
    def configuration() -> [options_v1.OptionSpec]:
        """TODO"""

        return [
            options_v1.OptionSpec("replicas", "number of replicas", 1, int)
        ]

    def _add_network_link(self, component: str, address: int):
        """TODO"""

        self.network_links.append((component, address))

    def _add_volume_link(self, volume: str, mount_point: str):
        """TODO"""

        self.volume_links.append((volume, mount_point))

    def _get_modules_path(self) -> str:
        """TODO"""

        return self.params["path"]

    def _add_requirements(self, requirements: [str]):
        """TODO"""

    def initialize(self):
        """TODO"""

        self.network_links = []
        self.volume_links = []

        self.version = '0.1'
        self.replicas = self.config['replicas']

    def inbound_interfaces(self) -> [component_v1.Interface]:
        """TODO"""

        return [
            interfaces.NetworkLink(add=self._add_network_link),
            interfaces.VolumeLink(add=self._add_volume_link),
            interfaces.PythonModulesPath(get=self._get_modules_path),
            interfaces.PythonRequirements(add=self._add_requirements)
        ]

    def outbound_interfaces(self) -> [component_v1.Interface]:
        """TODO"""

        return []

    def on_create(self):
        """TODO"""

        # copy templates

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: str) -> bool:
        """TODO"""

        self.artifacts = [
            f"{deployment}/component/{self.name}-{self.version}"
        ]

        return True

    def on_generate(self, deployment: str) -> bool:
        """TODO"""

        self.manifest = [
            tao.Task(self.name,
                     f"{deployment}/component/{self.name}-{self.version}",
                     self.network_links,
                     self.volume_links,
                     replicas=self.replicas)
        ]

        return True
