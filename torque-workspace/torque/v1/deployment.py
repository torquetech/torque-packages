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
                 buckets,
                 modified_buckets,
                 hooks: [typing.Callable],
                 load_bucket):
        self._buckets = buckets
        self._modified_buckets = modified_buckets
        self._hooks = hooks
        self._load_bucket = load_bucket

    def set_data(self, bucket: str, name: type, data: object):
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = {}

        self._modified_buckets.add(bucket)

        bucket = self._buckets[bucket]
        bucket[name] = data

    def get_data(self, bucket: str, name: str) -> object:
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = self._load_bucket(bucket)

        bucket = self._buckets[bucket]
        return bucket.get(name)

    def secret(self, object_name: str, secret_name: str, length: int = 16) -> str:
        """TODO"""

        name = f"{object_name}-{secret_name}"
        s = self.get_data("secrets", name)

        if not s:
            s = secrets.token_urlsafe(length)
            self.set_data("secrets", name, s)

        return s

    def add_hook(self, bucket: str, hook: typing.Callable):
        """TODO"""

        if bucket not in self._hooks:
            self._hooks[bucket] = []

        self._hooks[bucket].append(hook)


class Context:
    """TODO"""

    PARAMETERS = {
        "defaults": {},
        "schema": {}
    }

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
        # pylint: disable=R0913

        self.deployment_name = deployment_name
        self.configuration = configuration

        self._lock = threading.Lock()
        self._buckets = {}
        self._modified_buckets = set()
        self._hooks = {}

    def __enter__(self):
        self._lock.acquire()

        return _ContextData(self._buckets,
                            self._modified_buckets,
                            self._hooks,
                            self.load_bucket)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    def get_hooks(self, bucket: str):
        """TODO"""

        return self._hooks.get(bucket, [])

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

        raise exceptions.RuntimeError(f"{v1.utils.fqcn(self)}: no path defined for this context")
