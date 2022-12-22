# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import functools

from collections import namedtuple

from torque import environment
from torque import v1


Authorization = namedtuple("Authorization", [
    "database",
    "user",
    "password"
])

Service = namedtuple("Service", [
    "host",
    "port",
    "options"
])


class V1ImplementationInterface(v1.bond.Interface):
    """DOCSTRING"""

    def auth(self, database: str, user: str) -> v1.utils.Future[Authorization]:
        """DOCSTRING"""

    def service(self) -> v1.utils.Future[Service] | Service:
        """DOCSTRING"""


class V1SourceInterface(v1.component.SourceInterface):
    """DOCSTRING"""

    def auth(self, database: str, user: str) -> v1.utils.Future[Authorization]:
        """DOCSTRING"""

    def service(self) -> v1.utils.Future[Service] | Service:
        """DOCSTRING"""


class V1DestinationInterface(v1.component.DestinationInterface):
    """DOCSTRING"""

    def add(self,
            name: str,
            auth: v1.utils.Future[Authorization],
            service: v1.utils.Future[Service] | Service):
        """DOCSTRING"""


class V1Component(v1.component.Component):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "impl": {
                "interface": V1ImplementationInterface,
                "required": True
            }
        }

    def on_interfaces(self) -> [v1.component.Interface]:
        """DOCSTRING"""

        return [
            V1SourceInterface(auth=self.interfaces.impl.auth,
                              service=self.interfaces.impl.service)
        ]


class V1EnvironmentLink(environment.V1BaseLink):
    """DOCSTRING"""

    PARAMETERS = environment.V1BaseLink.PARAMETERS | {
        "defaults": {},
        "schema": {
            "database": str,
            "user": str
        }
    }

    @classmethod
    def on_requirements(cls):
        """DOCSTRING"""

        return super().on_requirements() | {
            "src": {
                "interface": V1SourceInterface,
                "required": True
            }
        }

    def _resolve_uri(self,
                     auth: v1.utils.Future[Authorization],
                     service: v1.utils.Future[Service] | Service) -> str:
        """DOCSTRING"""

        auth = v1.utils.resolve_futures(auth)
        service = v1.utils.resolve_futures(service)

        args = "&".join([f"{k}={v}" for k, v in service.options.items()])

        return f"postgres://{auth.user}:{auth.password}@{service.host}:{service.port}/{auth.database}?{args}"

    def on_apply(self):
        """DOCSTRING"""

        auth = self.interfaces.src.auth(self.parameters["database"],
                                        self.parameters["user"])

        service = self.interfaces.src.service()

        self.interfaces.dst.add(self._name(),
                                v1.utils.Future(functools.partial(self._resolve_uri,
                                                                  auth,
                                                                  service)))


class V1ServiceLink(v1.link.Link):
    """DOCSTRING"""

    PARAMETERS = {
        "defaults": {},
        "schema": {
            "database": str,
            "user": str
        }
    }

    @classmethod
    def on_requirements(cls):
        """DOCSTRING"""

        return {
            "src": {
                "interface": V1SourceInterface,
                "required": True
            },
            "dst": {
                "interface": V1DestinationInterface,
                "required": True
            }
        }

    def on_apply(self):
        """DOCSTRING"""

        self.interfaces.dst.add(self.source,
                                self.interfaces.src.auth(self.parameters["database"],
                                                         self.parameters["user"]),
                                self.interfaces.src.service())


repository = {
    "v1": {
        "components": [
            V1Component
        ],
        "links": [
            V1EnvironmentLink,
            V1ServiceLink
        ]
    }
}
