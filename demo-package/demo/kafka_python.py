# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import jinja2

from torque import v1

from demo import components
from demo import network
from demo import utils


class Link(network.Link):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return super().on_requirements() | {
            "kafka": {
                "interface": components.KafkaService,
                "required": True
            },
            "mod": {
                "interface": components.PythonModules,
                "required": True
            }
        }

    def on_create(self):
        """TODO"""

        super().on_create()

        template_path = f"{utils.module_path()}/templates/kafka_python.py.template"
        template = jinja2.Template(utils.load_file(template_path))

        target_path = f"{self.interfaces.mod.path()}/{self.source}.py"

        if os.path.exists(v1.utils.resolve_path(target_path)):
            raise RuntimeError(f"{target_path}: file already exists")

        with open(v1.utils.resolve_path(target_path), "w", encoding="utf8") as file:
            file.write(template.render(COMPONENT=self.source.upper()))
            file.write("\n")

        self.interfaces.mod.add_requirements(["kafka-python"])
