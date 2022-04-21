# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import jinja2

from torque import v1

from demo import interfaces
from demo import network
from demo import utils


class Link(network.Link):
    """TODO"""

    # pylint: disable=W0212
    _CONFIGURATION = v1.utils.merge_dicts(network.Link._CONFIGURATION, {
        "defaults": {
            "database": "postgres"
        },
        "schema": {
            "database": str
        }
    }, allow_overwrites=False)

    @classmethod
    def on_requirements(cls) -> [v1.utils.InterfaceRequirement]:
        """TODO"""

        return super().on_requirements() + [
            v1.utils.InterfaceRequirement(interfaces.PostgresService, "source", "pg"),
            v1.utils.InterfaceRequirement(interfaces.PythonModules, "destination", "mod"),
            v1.utils.InterfaceRequirement(interfaces.SecretLink, "destination", "sec"),
            v1.utils.InterfaceRequirement(interfaces.Environment, "destination", "env")
        ]

    def on_create(self):
        """TODO"""

        super().on_create()

        if not self.interfaces.pg:
            raise RuntimeError(f"{self.source}: incompatible component")

        if not self.interfaces.mod \
           or not self.interfaces.sec \
           or not self.interfaces.env:
            raise RuntimeError(f"{self.destination}: incompatible component")

        template = jinja2.Template(utils.load_file(f"{utils.module_path()}/templates/psycopg.py.template"))
        target_path = f"{self.interfaces.mod.path()}/{self.source}.py"

        if os.path.exists(v1.utils.resolve_path(target_path)):
            raise RuntimeError(f"{target_path}: file already exists")

        with open(v1.utils.resolve_path(target_path), "w", encoding="utf8") as file:
            file.write(template.render(COMPONENT=self.source.upper()))
            file.write("\n")

        self.interfaces.mod.add_requirements(["psycopg"])

    def on_apply(self, deployment: v1.deployment.Deployment):
        """TODO"""

        super().on_apply(deployment)

        source = self.source.upper()
        secret = self.interfaces.pg.admin()

        self.interfaces.env.add(f"{source}_PSYCOPG_DB", self.configuration["database"])
        self.interfaces.sec.add(f"{source}_PSYCOPG_USER", "user", secret)
        self.interfaces.sec.add(f"{source}_PSYCOPG_PASSWORD", "password", secret)
