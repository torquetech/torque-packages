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

    def on_create(self):
        """TODO"""

        network.Link.on_create(self)

        if not self.source.has_interface(interfaces.PostgresService):
            raise RuntimeError(f"{self.source.name}: incompatible component")

        if not self.destination.has_interface(interfaces.PythonModules):
            raise RuntimeError(f"{self.destination.name}: incompatible component")

        if not self.destination.has_interface(interfaces.Secret):
            raise RuntimeError(f"{self.destination.name}: incompatible component")

        if not self.destination.has_interface(interfaces.Environment):
            raise RuntimeError(f"{self.destination.name}: incompatible component")

        template = jinja2.Template(utils.load_file(f"{utils.module_path()}/templates/psycopg2.py.template"))

        modules = self.destination.interface(interfaces.PythonModules)
        target_path = f"{modules.path()}/{self.source.name}.py"

        if os.path.exists(v1.utils.resolve_path(target_path)):
            raise RuntimeError(f"{target_path}: file already exists")

        with open(v1.utils.resolve_path(target_path), "w", encoding="utf8") as file:
            file.write(template.render(COMPONENT=self.source.name.upper()))
            file.write("\n")

        modules.add_requirements(["psycopg2"])

    def on_apply(self, deployment: v1.deployment.Deployment) -> bool:
        """TODO"""

        if not network.Link.on_apply(self, deployment):
            return False

        source = self.source.name.upper()

        src = self.source.interface(interfaces.PostgresService)
        secret = src.admin()

        sec = self.destination.interface(interfaces.Secret)
        sec.add(f"{source}_PSYCOPG2_USER", secret, "user")
        sec.add(f"{source}_PSYCOPG2_PASSWORD", secret, "password")

        env = self.destination.interface(interfaces.Environment)
        env.add(f"{source}_PSYCOPG2_DB", self.configuration["database"])

        return True
