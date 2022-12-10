# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import secrets
import threading
import typing

from . import exceptions
from . import utils


class _ContextData:
    """TODO"""

    def __init__(self,
                 buckets: dict[str, object],
                 load_bucket: typing.Callable):
        self._buckets = buckets
        self._load_bucket = load_bucket

    def _get(self, bucket: str) -> object:
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = self._load_bucket(bucket)

        return self._buckets[bucket]

    def set_data(self, bucket: str, name: type, data: object):
        """TODO"""

        bucket = self._get(bucket)
        bucket[name] = data

    def delete_data(self, bucket: str, name: str):
        """TODO"""

        bucket = self._get(bucket)
        return bucket.pop(name, None)

    def get_data(self, bucket: str, name: str) -> object:
        """TODO"""

        bucket = self._get(bucket)
        return bucket.get(name)

    def set_secret_data(self, object_name: str, secret_name: str, data: object):
        """TODO"""

        name = f"{object_name}-{secret_name}"
        self.set_data("secrets", name, data)

    def delete_secret_data(self, object_name: str, secret_name: str):
        """TODO"""

        name = f"{object_name}-{secret_name}"
        return self.delete_data("secrets", name)

    def get_secret_data(self, object_name: str, secret_name: str) -> object:
        """TODO"""

        name = f"{object_name}-{secret_name}"
        return self.get_data("secrets", name)

    def secret(self, object_name: str, secret_name: str, length: int = 16) -> object:
        """TODO"""

        s = self.get_secret_data(object_name, secret_name)

        if not s:
            s = secrets.token_urlsafe(length)
            self.set_secret_data(object_name, secret_name, s)

        return s


class Context:
    """TODO"""

    CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return utils.validate_schema(cls.CONFIGURATION["schema"],
                                     cls.CONFIGURATION["defaults"],
                                     configuration)

    def __init__(self, deployment_name: str, configuration: dict[str, object]):
        self.deployment_name = deployment_name
        self.configuration = configuration

        self._lock = threading.Lock()
        self._buckets = {}

    def __enter__(self):
        self._lock.acquire()

        return _ContextData(self._buckets, self.load_bucket)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    def store(self):
        """TODO"""

        for name, data in self._buckets.items():
            self.store_bucket(name, data)

    def load_bucket(self, name: str) -> dict[str, object]:
        """TODO"""

    def store_bucket(self, name: str, data: dict[str, object]):
        """TODO"""

    def path(self) -> str:
        """TODO"""

        raise exceptions.RuntimeError(f"{utils.fqcn(self)}: no path defined for this context")

    def external_path(self) -> str:
        """TODO"""

        return self.path()
