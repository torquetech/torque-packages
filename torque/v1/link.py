# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from . import deployment
from . import utils


class Link:
    """TODO"""

    def __init__(self,
                 name: str,
                 parameters: dict[str, object],
                 configuration: dict[str, object],
                 context: deployment.Context,
                 bonds: object,
                 source: str,
                 destination: str):
        # pylint: disable=R0913

        self.name = name
        self.parameters = parameters
        self.configuration = configuration
        self.context = context
        self.bonds = bonds
        self.source = source
        self.destination = destination

    @classmethod
    def on_parameters(cls, parameters: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_parameters: not implemented")

    @classmethod
    def on_configuration(cls, configuration: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")

    def on_create(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_create: not implemented")

    def on_remove(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_remove: not implemented")

    def on_build(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_build: not implemented")

    def on_apply(self):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_apply: not implemented")
