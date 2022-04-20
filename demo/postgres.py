# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1

from demo import interfaces
from demo import providers
from demo import utils


class Component(v1.component.Component):
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

        self._volume_links = []

        self._service_link = None
        self._secret_link = None

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        return v1.utils.validate_schema(cls._PARAMETERS["schema"],
                                        cls._PARAMETERS["defaults"],
                                        parameters)

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        defaults = v1.utils.merge_dicts(cls._CONFIGURATION["defaults"], {
            "password": utils.generate_password()
        })

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        defaults,
                                        configuration)

    def _image(self) -> str:
        return f"postgres:{self.configuration['version']}"

    def _add_volume_link(self, name: str, mount_path: str, link: v1.utils.Future[object]):
        """TODO"""

        link = providers.VolumeLink(name, mount_path, link)
        self._volume_links.append(link)

    def _link(self) -> v1.utils.Future[object]:
        """TODO"""

        return self._service_link

    def _admin(self) -> v1.utils.Future[object]:
        """TODO"""

        return self._secret_link

    def on_interfaces(self) -> [v1.component.Interface]:
        """TODO"""

        return [
            interfaces.VolumeLink(add=self._add_volume_link),
            interfaces.PostgresService(link=self._link, admin=self._admin)
        ]

    def on_create(self):
        """TODO"""

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment):
        """TODO"""

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        secrets = deployment.provider(providers.SecretsProvider)
        self._secret_link = secrets.create(f"{self.name}_admin", [
            providers.KeyValue("user", "postgres"),
            providers.KeyValue("password", self.configuration["password"])
        ])

        services = deployment.provider(providers.ServicesProvider)
        self._service_link = services.create(self.name, [5432], None)

        env = [
            providers.KeyValue("PGDATA", "/data")
        ]

        secret_links = [
            providers.SecretLink("POSTGRES_PASSWORD", "password", self._secret_link)
        ]

        deployments = deployment.provider(providers.DeploymentsProvider)
        deployments.create(self.name,
                           self._image(),
                           None,
                           None,
                           None,
                           env,
                           None,
                           self._volume_links,
                           secret_links,
                           1)
