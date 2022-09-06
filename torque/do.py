# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import typing

from torque import v1
from torque import dolib


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "token": "invalid_token",
            "quiet": True
        },
        "schema": {
            "token": str,
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

        self._params = None

        self._current_state = {}
        self._new_state = {}

    def _connect(self) -> dolib.Client:
        """TODO"""

        return dolib.connect(self._params["endpoint"],
                             self.configuration["token"])

    def _load_params(self, context: v1.deployment.Context):
        """TODO"""

        with context as ctx:
            self._params = ctx.get_data("state", self, "parameters")

            if not self._params:
                raise RuntimeError(f"digital ocean provider not initialized")

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

        self._load_params(context)

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

        self._load_params(context)

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

        parser = argparse.ArgumentParser(prog="", description="digital ocean command line interface.")

        parser.add_argument("--endpoint",
                            default="https://api.digitalocean.com",
                            help="digital ocean api endpoint to use, default: %(default)s")

        parser.add_argument("region",
                            metavar="REGION",
                            help="digital ocean region to use")

        args = parser.parse_args(argv)

        with context as ctx:
            if ctx.get_data("state", self, "parameters"):
                raise RuntimeError(f"parameters cannot be changed")

            params = {
                "endpoint": args.endpoint,
                "region": args.region,
            }

            ctx.set_data("state", self, "parameters", params)

    def region(self) -> str:
        """TODO"""

        return self._params["region"]

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
