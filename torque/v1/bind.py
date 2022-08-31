# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from . import deployment
from . import provider
from . import utils


class Bind:
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
