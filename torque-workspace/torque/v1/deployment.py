# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import secrets
import threading

from . import utils


class _ContextContext:
    """TODO"""

    def __init__(self, buckets, modified_buckets, load_bucket):
        self._buckets = buckets
        self._modified_buckets = modified_buckets
        self._load_bucket = load_bucket

    def _set_data(self, bucket: str, name: type, data: object):
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = {}

        self._modified_buckets.add(bucket)

        bucket = self._buckets[bucket]
        bucket[name] = data

    def _get_data(self, bucket: str, name: str) -> object:
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = self._load_bucket(bucket)

        bucket = self._buckets[bucket]
        return bucket.get(name)

    def set_data(self, bucket: str, cls: type, data: object):
        """TODO"""

        self._set_data(bucket, utils.fqcn(cls), data)

    def get_data(self, bucket: str, cls: type) -> object:
        """TODO"""

        return self._get_data(bucket, utils.fqcn(cls))

    def secret(self, cls: type, name: str, length: int = 16) -> str:
        """TODO"""

        name = f"{utils.fqcn(cls)}-{name}"
        s = self._get_data("secrets", name)

        if not s:
            s = secrets.token_urlsafe(length)
            self._set_data("secrets", name, s)

        return s


class Context:
    """TODO"""

    _PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: object) -> object:
        """TODO"""

        return utils.validate_schema(cls._CONFIGURATION["schema"],
                                     cls._CONFIGURATION["defaults"],
                                     configuration)

    def __init__(self, deployment_name: str, configuration: dict[str, object]):
        # pylint: disable=R0913

        self.deployment_name = deployment_name
        self.configuration = configuration

        self._lock = threading.Lock()
        self._buckets = {}
        self._modified_buckets = set()

    def __enter__(self):
        self._lock.acquire()

        return _ContextContext(self._buckets, self._modified_buckets, self.load_bucket)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    def store(self):
        """TODO"""

        for name, data in self._buckets.items():
            if name in self._modified_buckets:
                self.store_bucket(name, data)

    def load_bucket(self, name: str) -> dict[str, object]:
        """TODO"""

    def store_bucket(self, name: str, data: dict[str, object]):
        """TODO"""

    def path(self) -> str:
        """TODO"""
