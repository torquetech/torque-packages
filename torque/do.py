# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import typing

from torque import v1
from torque import dolib


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "endpoint": "https://api.digitalocean.com",
            "token": "invalid_token",
            "region": "nyc1",
            "quiet": True
        },
        "schema": {
            "endpoint": str,
            "token": str,
            "region": str,
            "quiet": bool
        }
    }

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_state = {}
        self._new_state = {}

    def _connect(self) -> dolib.Client:
        """TODO"""

        return dolib.connect(self.configuration["endpoint"],
                             self.configuration["token"])

    def _load_state(self, context: v1.deployment.Context) -> dict[str, object]:
        """TODO"""

        with context as ctx:
            self._current_state = ctx.get_data("state", self, "state") or {}


    def _store_state(self, context: v1.deployment.Context):
        """TODO"""

        with context as ctx:
            ctx.set_data("state", self, "state", self._current_state)

    def on_apply(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

        client = self._connect()
        self._load_state(context)

        try:
            dolib.apply(client,
                        self._current_state,
                        self._new_state,
                        self.configuration["quiet"])

        finally:
            self._store_state(context)

    def on_delete(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

        client = self._connect()
        self._load_state(context)

        try:
            dolib.apply(client,
                        self._current_state,
                        self._new_state,
                        self.configuration["quiet"])

        finally:
            self._store_state(context)

    def on_command(self, context: v1.deployment.Context, argv: [str]):
        """TODO"""

    def region(self) -> str:
        """TODO"""

        return self.configuration["region"]

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            name = f"{obj['kind']}/{obj['name']}"

            if name in self._new_state:
                raise RuntimeError(f"{name}: digital ocean object already exists")

            self._new_state[name] = obj

    def future(self, name: str, func: typing.Callable) -> v1.utils.Future:
        """TODO"""

        def resolve_future():
            return func(self._current_state[name])

        return v1.utils.Future(resolve_future)


repository = {
    "v1": {
        "interfaces": [],
        "providers": {
            "torquetech.io/do": Provider
        }
    }
}
