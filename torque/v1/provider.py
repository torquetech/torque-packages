# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from . import deployment
from . import utils


class Provider:
    """TODO"""

    def __init__(self,
                 configuration: object,
                 binds: object):
        self.configuration = configuration
        self.binds = binds

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")

    def on_apply(self, context: deployment.Context, dry_run: bool):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_apply: not implemented")

    def on_delete(self, context: deployment.Context, dry_run: bool):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_delete: not implemented")

    def on_command(self, context: deployment.Context, argv: [str]):
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(self)}: on_command: not implemented")


class Interface:
    """TODO"""

    def __init__(self,
                 configuration: object,
                 provider: Provider,
                 labels: [str],
                 binds: object,
                 context: deployment.Context):
        self.configuration = configuration
        self.provider = provider
        self.labels = labels
        self.binds = binds
        self.context = context

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")
