# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from . import deployment
from . import utils


class Provider:
    """TODO"""

    def __init__(self,
                 configuration: object,
                 bonds: object):
        self.configuration = configuration
        self.bonds = bonds

        self._lock = threading.Lock()
        self._data = {}

    def set_data(self, cls: type, name: str, data: object):
        """TODO"""

        with self._lock:
            cls = utils.fqcn(cls)

            if cls not in self._data:
                self._data[cls] = {}

            self._data[cls][name] = data

    def get_data(self, cls: type, name: str) -> object:
        """TODO"""

        with self._lock:
            cls = utils.fqcn(cls)

            if cls not in self._data:
                return None

            return self._data[cls].get(name)

    def apply(self, context: deployment.Context, dry_run: bool):
        """TODO"""

        self.on_apply(context, dry_run)

    def delete(self, context: deployment.Context, dry_run: bool):
        """TODO"""

        self.on_delete(context, dry_run)

    def command(self, context: deployment.Context, argv: [str]):
        """TODO"""

        self.on_command(context, argv)

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
