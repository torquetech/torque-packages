# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading

from . import deployment
from . import utils


class _ProviderContext:
    """TODO"""

    def __init__(self,
                 data: dict[str, object]):
        self._data = data

    def set_data(self, cls: type, name: str, data: object):
        """TODO"""

        cls_type = utils.fqcn(cls)

        if cls_type not in self._data:
            self._data[cls_type] = {}

        self._data[cls_type][name] = data

    def get_data(self, cls: type, name: str) -> object:
        """TODO"""

        cls_type = utils.fqcn(cls)

        if cls_type not in self._data:
            return None

        return self._data[cls_type].get(name)


class Provider:
    """TODO"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    def __init__(self,
                 configuration: object,
                 context: deployment.Context,
                 interfaces: object):
        self.configuration = configuration
        self.context = context
        self.interfaces = interfaces

        self._lock = threading.Lock()
        self._data = {}

    def __enter__(self):
        self._lock.acquire()

        return _ProviderContext(self._data)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return utils.validate_schema(cls.CONFIGURATION["schema"],
                                     cls.CONFIGURATION["defaults"],
                                     configuration)

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {}
