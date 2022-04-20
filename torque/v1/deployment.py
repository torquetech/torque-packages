# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import shutil

from . import metadata
from . import provider
from . import utils


class Deployment:
    """TODO"""

    def __init__(self, metadata: metadata.Deployment, providers: [provider.Provider]):
        self.metadata = metadata

        self._interfaces = {}

        for p in providers:
            if not issubclass(p.__class__, provider.Provider):
                raise RuntimeError(f"{utils.fqcn(p)}: invalid provider")

            cls = p.__class__

            while cls is not provider.Provider:
                if len(cls.__bases__) != 1:
                    raise RuntimeError(f"{utils.fqcn(cls)}: multiple inheritance not supported")

                self._interfaces[utils.fqcn(cls)] = p
                cls = cls.__bases__[0]

        if os.path.exists(self.metadata.path):
            for path in os.listdir(self.metadata.path):
                path = f"{self.metadata.path}/{path}"

                if os.path.isdir(path):
                    shutil.rmtree(path)

                else:
                    os.unlink(path)

        else:
            os.makedirs(self.metadata.path)

    def provider(self, cls: type) -> provider.Provider:
        """TODO"""

        name = utils.fqcn(cls)

        if name not in self._interfaces:
            raise RuntimeError(f"{name}: provider not implemented")

        return self._interfaces[name]


def create(metadata: metadata.Deployment, providers: [provider.Provider]) -> Deployment:
    """TODO"""

    return Deployment(metadata, providers)
