# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import jinja2
import schema

from torque import v1

from demo import interfaces
from demo import utils


class Link(v1.link.Link):
    """TODO"""

    @staticmethod
    def validate_parameters(parameters: object) -> object:
        """TODO"""

        _DEFAULT_PARAMETERS = {
        }

        _PARAMETERS_SCHEMA = schema.Schema({
        })

        return utils.validate_schema("parameters",
                                     parameters,
                                     _DEFAULT_PARAMETERS,
                                     _PARAMETERS_SCHEMA)

    @staticmethod
    def validate_configuration(configuration: object) -> object:
        """TODO"""

        _DEFAULT_CONFIGURATION = {
            "database": "postgres"
        }

        _CONFIGURATION_SCHEMA = schema.Schema({
            "database": str
        })

        return utils.validate_schema("configuration",
                                     configuration,
                                     _DEFAULT_CONFIGURATION,
                                     _CONFIGURATION_SCHEMA)

    def on_create(self):
        """TODO"""

        if not self.source.has_outbound_interface(interfaces.PostgresService):
            raise RuntimeError(f"{self.source.name}: incompatible component")

        if not self.destination.has_inbound_interface(interfaces.PythonModules):
            raise RuntimeError(f"{self.destination.name}: incompatible component")

        template = jinja2.Template(utils.load_file(f"{utils.module_path()}/templates/psycopg2.py.template"))

        with self.destination.inbound_interface(interfaces.PythonModules) as dst:
            target_path = f"{dst.path()}/{self.source.name}.py"

            if os.path.exists(v1.utils.resolve_path(target_path)):
                raise RuntimeError(f"{target_path}: file already exists")

            with open(v1.utils.resolve_path(target_path), "w", encoding="utf8") as file:
                file.write(template.render(COMPONENT=self.source.name.upper()))
                file.write("\n")

            dst.add_requirements(["psycopg2"])

    def on_remove(self):
        """TODO"""

    def on_build(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        return True

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        with self.source.outbound_interface(interfaces.PostgresService) as src:
            link = src.link()
            secret = src.admin()

        with self.destination.inbound_interface(interfaces.NetworkLink) as dst:
            dst.add(link)

        source = self.source.name.upper()

        with self.destination.inbound_interface(interfaces.Secret) as dst:
            dst.add(f"PSYCOPG2_{source}_USER", secret, "user")
            dst.add(f"PSYCOPG2_{source}_PASSWORD", secret, "password")

        with self.destination.inbound_interface(interfaces.Environment) as dst:
            dst.add(f"PSYCOPG2_{source}_DB", self.configuration["database"])

        return True
