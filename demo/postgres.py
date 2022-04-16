# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import schema

from torque import v1

from demo import interfaces
from demo import utils


class Service(v1.component.Component):
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    _CONFIGURATION = {
        "defaults": {
            "version": "14.2",
            "password": None
        },
        "schema": {
            "version": str,
            "password": str
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._service_link = None
        self._secret = None
        self._volume_links = []

    @classmethod
    def validate_parameters(cls, parameters: object) -> object:
        """TODO"""

        return utils.validate_schema("parameters",
                                     cls._PARAMETERS,
                                     parameters)

    @classmethod
    def validate_configuration(cls, configuration: object) -> object:
        """TODO"""

        _configuration = v1.utils.merge_dicts(cls._CONFIGURATION, {
            "defaults": {
                "password": utils.generate_password()
            }
        })

        return utils.validate_schema("configuration",
                                     _configuration,
                                     configuration)

    def _image(self) -> str:
        return f"postgres:{self.configuration['version']}"

    def _add_volume_link(self, mount_point: str, link: v1.interface.Future):
        """TODO"""

        self._volume_links.append((mount_point, link))

    def _link(self) -> v1.interface.Future[interfaces.Provider.NetworkLink]:
        """TODO"""

        return self._service_link

    def _admin(self) -> v1.interface.Future[str]:
        """TODO"""

        return self._secret

    def interfaces(self) -> [v1.interface.Interface]:
        """TODO"""

        return [
            interfaces.VolumeLink(add=self._add_volume_link),
            interfaces.PostgresService(link=self._link, admin=self._admin)
        ]

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        return True

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        env = [
            interfaces.Provider.KeyValue("PGDATA", "/data")
        ]

        with interfaces.Provider(deployment) as provider:
            self._secret = provider.create_secret(f"{self.name}_admin", [
                interfaces.Provider.KeyValue("user", "postgres"),
                interfaces.Provider.KeyValue("password", self.configuration["password"])
            ])

            self._service_link = provider.create_service(self.name, [5432], None)

            secrets = [
                interfaces.Provider.Secret("POSTGRES_PASSWORD", self._secret, "password")
            ]

            provider.create_deployment(self.name,
                                       self._image(),
                                       None,
                                       None,
                                       None,
                                       env,
                                       None,
                                       self._volume_links,
                                       secrets,
                                       1)

        return True
