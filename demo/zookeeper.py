# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import components
from demo import providers
from demo import types
from demo import volume
from demo import utils


class Component(v1.component.Component):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_parameters(cls, parameters: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._PARAMETERS["schema"],
                                        cls._PARAMETERS["defaults"],
                                        parameters)

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "services": {
                "interface": providers.Services,
                "required": True
            },
            "deployments": {
                "interface": providers.Deployments,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._volume_links = []
        self._service_link = None

    def _add_volume_link(self, name: str, mount_path: str, link: utils.Future[object]):
        """TODO"""

        link = types.VolumeLink(name, mount_path, link)
        self._volume_links.append(link)

    def _link(self) -> utils.Future[object]:
        """TODO"""

        return self._service_link

    def _data_path(self) -> str:
        """TODO"""

        return "/bitnami/zookeeper"

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.VolumeLink(add=self._add_volume_link),
            components.ZookeeperService(link=self._link,
                                        data_path=self._data_path)
        ]

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, context: v1.deployment.Context):
        """TODO"""

    def on_apply(self, context: v1.deployment.Context):
        """TODO"""

        self._service_link = self.bonds.services.create(self.name, "tcp", 2181, 2181)

        env = [
            types.KeyValue("ALLOW_ANONYMOUS_LOGIN", "yes")
        ]

        self.bonds.deployments.create(self.name,
                                      "bitnami/zookeeper:latest",
                                      None,
                                      None,
                                      None,
                                      env,
                                      None,
                                      None,
                                      self._volume_links,
                                      None)


class DataLink(volume.Link):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return super().on_requirements() | {
            "zk": {
                "interface": components.ZookeeperService,
                "bind_to": "destination",
                "required": True
            },
        }

    def on_apply(self, context: v1.deployment.Context):
        """TODO"""

        self.bonds.dst.add(self.source,
                           self.bonds.zk.data_path(),
                           self.bonds.src.link())
