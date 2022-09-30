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
        self._zookeeper_link = None
        self._service_link = None

    def _image(self) -> str:
        return f"postgres:{self.configuration['version']}"

    def _add_volume_link(self, name: str, mount_path: str, link: utils.Future[object]):
        """TODO"""

        link = types.VolumeLink(name, mount_path, link)
        self._volume_links.append(link)

    def _link(self) -> utils.Future[object]:
        """TODO"""

        return self._service_link

    def _data_path(self) -> str:
        """TODO"""

        return "/bitnami/kafka"

    def _zookeeper(self, link: utils.Future[object]):
        """TODO"""

        if self._zookeeper_link:
            raise RuntimeError(f"{self.name}: only one zookeeper connection allowed")

        self._zookeeper_link = link

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.VolumeLink(add=self._add_volume_link),
            components.Service(link=self._link),
            components.KafkaService(link=self._link),
            components.Kafka(data_path=self._data_path,
                             zookeeper=self._zookeeper)
        ]

    def on_apply(self):
        """TODO"""

        self._service_link = self.interfaces.services.create(self.name, "tcp", 9092, 9092)

        zk_link = self._zookeeper_link.get()

        env = [
            types.KeyValue("KAFKA_CFG_ZOOKEEPER_CONNECT", f"{zk_link[1]}:{zk_link[2]}"),
            types.KeyValue("ALLOW_PLAINTEXT_LISTENER", "yes")
        ]

        self.interfaces.deployments.create(self.name,
                                           "bitnami/kafka:latest",
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

    PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return super().on_requirements() | {
            "kafka": {
                "interface": components.Kafka,
                "required": True
            },
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.dst.add(self.source,
                                self.interfaces.kafka.data_path(),
                                self.interfaces.src.link())


class ZookeeperLink(v1.link.Link):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "zk": {
                "interface": components.ZookeeperService,
                "required": True
            },
            "kafka": {
                "interface": components.Kafka,
                "required": True
            }
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.kafka.zookeeper(self.interfaces.zk.link())
