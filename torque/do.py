# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import functools

from torque import v1
from torque import dolib


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "token": None,
            "quiet": True
        },
        "schema": {
            "token": v1.schema.Or(str, None),
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
        self._client = None

        self._project = None
        self._vpc = None

        self._current_state = {}
        self._new_state = {}

    def _connect(self) -> dolib.Client:
        """TODO"""

        do_token = self.configuration["token"]

        if not do_token:
            do_token = os.getenv("DO_TOKEN")

        self._client = dolib.connect(self._params["endpoint"], do_token)

    def _load_params(self):
        """TODO"""

        with self.context as ctx:
            self._params = ctx.get_data("parameters", self)

            if not self._params:
                raise RuntimeError(f"digital ocean provider not initialized")

    def _load_state(self) -> dict[str, object]:
        """TODO"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", self) or {}


    def _store_state(self):
        """TODO"""

        with self.context as ctx:
            ctx.set_data("state", self, self._current_state)

    def on_apply(self, dry_run: bool):
        """TODO"""

        self._load_params()
        self._connect()

        self._load_state()

        self._project = dolib.setup_project(self._client, self._params["project_name"])
        self._vpc = dolib.setup_vpc(self._client, self._params["vpc_name"], self._params["region"])

        try:
            dolib.apply(self._client,
                        self._current_state,
                        self._new_state,
                        self.configuration["quiet"])

        finally:
            self._store_state()

    def on_delete(self, dry_run: bool):
        """TODO"""

        self._load_params()
        self._connect()

        self._load_state()

        try:
            dolib.apply(self._client,
                        self._current_state,
                        {},
                        self.configuration["quiet"])

        finally:
            self._store_state()

    def on_command(self, argv: [str]):
        """TODO"""

        parser = argparse.ArgumentParser(prog="", description="digital ocean command line interface.")

        parser.add_argument("--endpoint",
                            default="https://api.digitalocean.com",
                            help="digital ocean api endpoint to use, default: %(default)s")

        parser.add_argument("region",
                            metavar="REGION",
                            help="digital ocean region to use")

        args = parser.parse_args(argv)

        with self.context as ctx:
            if ctx.get_data("parameters", self):
                raise RuntimeError(f"parameters cannot be changed")

            params = {
                "endpoint": args.endpoint,
                "region": args.region,
                "project_name": self.context.deployment_name,
                "vpc_name": f"{self.context.deployment_name}-{args.region}"
            }

            ctx.set_data("parameters", self, params)

    def client(self) -> dolib.Client:
        """TODO"""

        return self._client

    def _resolve_project_id(self):
        if not self._project:
            return "<project_id>"

        return self._project["id"]

    def _resolve_vpc_id(self):
        if not self._vpc:
            return "<vpc_id>"

        return self._vpc["id"]

    def _resolve_region(self):
        if not self._params:
            return "<region>"

        return self._params["region"]

    def project_id(self) -> v1.utils.Future[str]:
        """TODO"""

        return v1.utils.Future(self._resolve_project_id)

    def vpc_id(self) -> v1.utils.Future[str]:
        """TODO"""

        return v1.utils.Future(self._resolve_vpc_id)

    def object_id(self, name: str) -> v1.utils.Future[str]:
        """TODO"""

        def resolve_object_id():
            """TODO"""

            if name not in self._current_state:
                return f"<{name}_id>"

            return self._current_state[name]["metadata"]["id"]

        return v1.utils.Future(resolve_object_id)

    def region(self) -> str:
        """TODO"""

        return v1.utils.Future(self._resolve_region)

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            name = f"{obj['kind']}/{obj['name']}"

            if name in self._new_state:
                raise RuntimeError(f"{name}: digital ocean object already exists")

            self._new_state[name] = obj


repository = {
    "v1": {
        "providers": {
            "torquetech.io/do": Provider
        }
    }
}
