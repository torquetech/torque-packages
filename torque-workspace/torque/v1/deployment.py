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
                 hooks: [typing.Callable],
                 load_bucket: typing.Callable):
        self._buckets = buckets
        self._hooks = hooks
        self._load_bucket = load_bucket

    def _find_ndx(self, hooks: list, obj: object):
        """TODO"""

        for i, hook in enumerate(hooks):
            if obj == hook.__self__.__class__:
                return i

        return len(hooks)

    def set_data(self, bucket: str, name: type, data: object):
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = {}

        bucket = self._buckets[bucket]
        bucket[name] = data

    def delete_data(self, bucket: str, name: str):
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = self._load_bucket(bucket)

        bucket = self._buckets[bucket]
        return bucket.pop(name, None)

    def get_data(self, bucket: str, name: str) -> object:
        """TODO"""

        if bucket not in self._buckets:
            self._buckets[bucket] = self._load_bucket(bucket)

        bucket = self._buckets[bucket]
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

    def add_hook(self, bucket: str, hook: typing.Callable, **kwargs):
        """TODO"""

        if bucket not in self._hooks:
            self._hooks[bucket] = []

        hooks = self._hooks[bucket]
        add_before = kwargs.get("add_before", None)

        if add_before:
            ndx = self._find_ndx(hooks, add_before)

        else:
            ndx = len(hooks)

        hooks.insert(ndx, hook)


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
        self._hooks = {}

    def __enter__(self):
        self._lock.acquire()

        return _ContextData(self._buckets,
                            self._hooks,
                            self.load_bucket)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._lock.release()

    def run_hooks(self, bucket: str, **kwargs):
        """TODO"""

        quiet = kwargs.get("quiet", True)
        reverse = kwargs.get("reverse", False)
        op = kwargs.get("op", bucket)

        hooks = self._hooks.get(bucket, [])

        if reverse:
            hooks = reversed(hooks)

        for hook in hooks:
            if not quiet:
                print(f"{op} {hook.__module__}...")

            hook()

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
