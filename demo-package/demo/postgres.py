# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import components
from demo import providers
from demo import types
from demo import utils
from demo import volume


class Component(v1.component.Component):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "version": "14.2"
        },
        "schema": {
            "version": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {
            "secrets": {
                "interface": providers.Secrets,
                "required": True
            },
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
        self._secret_link = None

    def _image(self) -> str:
        return f"postgres:{self.configuration['version']}"

    def _add_volume_link(self, name: str, mount_path: str, link: utils.Future[object]):
        """TODO"""

        link = types.VolumeLink(name, mount_path, link)
        self._volume_links.append(link)

    def _link(self) -> utils.Future[object]:
        """TODO"""

        return self._service_link

    def _admin(self) -> utils.Future[object]:
        """TODO"""

        return self._secret_link

    def _data_path(self) -> str:
        """TODO"""

        return "/data"

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            components.VolumeLink(add=self._add_volume_link),
            components.Service(link=self._link),
            components.PostgresService(link=self._link,
                                       admin=self._admin),
            components.Postgres(data_path=self._data_path)
        ]

    def on_apply(self):
        """TODO"""

        with self.context as ctx:
            password = ctx.secret(self.name, "postgres")

        self._secret_link = self.interfaces.secrets.create(f"{self.name}_admin", [
            types.KeyValue("user", "postgres"),
            types.KeyValue("password", password)
        ])

        self._service_link = self.interfaces.services.create(self.name, "tcp", 5432, 5432)

        env = [
            types.KeyValue("PGDATA", f"/data/{self.configuration['version']}")
        ]

        secret_links = [
            types.SecretLink("POSTGRES_PASSWORD", "password", self._secret_link)
        ]

        self.interfaces.deployments.create(self.name,
                                           self._image(),
                                           None,
                                           None,
                                           None,
                                           env,
                                           None,
                                           None,
                                           self._volume_links,
                                           secret_links)


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
            "pg": {
                "interface": components.Postgres,
                "required": True
            },
        }

    def on_apply(self):
        """TODO"""

        self.interfaces.dst.add(self.source,
                                self.interfaces.pg.data_path(),
                                self.interfaces.src.link())
