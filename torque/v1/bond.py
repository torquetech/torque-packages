# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from . import deployment
from . import provider
from . import utils


class Bond:
    """TODO"""

    def __init__(self,
                 provider: provider.Provider,
                 parameters: dict,
                 configuration: dict,
                 context: deployment.Context,
                 bonds: object):
        self.provider = provider
        self.parameters = parameters
        self.configuration = configuration
        self.context = context
        self.bonds = bonds

    @classmethod
    def on_parameters(cls, parameters: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_parameters: not implemented")

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_configuration: not implemented")

    @classmethod
    def on_requirements(cls) -> object:
        """TODO"""

        raise RuntimeError(f"{utils.fqcn(cls)}: on_requirements: not implemented")
