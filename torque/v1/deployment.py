# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import shutil
import threading

from . import interface
from . import utils


class Deployment:
    """TODO"""

    def __init__(self, name: str, profile: str, dry_run: bool, providers: "[provider.Provider]"):
        self.name = name
        self.profile = profile
        self.dry_run = dry_run
        self.path = f"{utils.torque_dir()}/local/deployments/{name}"

        self._providers = providers
        self._lock = threading.Lock()
        self._interfaces = {}

        if os.path.exists(self.path):
            for path in os.listdir(self.path):
                path = f"{self.path}/{path}"

                if os.path.isdir(path):
                    shutil.rmtree(path)

                else:
                    os.unlink(path)

        else:
            os.makedirs(self.path)

    def _interface(self, cls: type, labels: [str]) -> interface.Context:
        """TODO"""

        name = utils.fqcn(cls)

        if name in self._interfaces:
            return self._interfaces[name].interface(cls)

        for provider in self._providers:
            if not provider.has_interface(cls):
                continue

            return provider.interface(cls)

        return interface.Context(self._lock, None)

    def interface(self, cls: type, labels: [str]) -> interface.Context:
        """TODO"""

        with self._lock:
            return self._interface(cls, labels)


def create(name: str, profile: str, dry_run: bool, providers: "[provider.Provider]") -> Deployment:
    """TODO"""

    return Deployment(name, profile, dry_run, providers)
