# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import base64

from torque import v1
from torque import container_registry
from torque import do
from torque import dolib


class _V2ContainerRegistry:
    """TODO"""

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/registry", new_obj["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        res = client.get("v2/registry/docker-credentials?"
                         "read_write=true")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["auths"]
        data = list(data.items())

        if len(data) != 1:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: invalid response")

        data = data[0]

        server = data[0]
        auth = data[1]["auth"]

        auth = auth.encode()
        auth = base64.b64decode(auth)
        auth = auth.decode()

        n = auth.index(":")

        username = auth[:n]
        password = auth[n+1:]

        return new_obj | {
            "metadata": {
                "server": server,
                "username": username,
                "password": password
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot container registry")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        # pylint: disable=W0613

        """TODO"""

        client.delete("v2/registry")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class Provider(v1.provider.Provider):
    """TODO"""

    PARAMETERS = {
        "defaults": {
            "subscription_tier_slug": "starter"
        },
        "schema": {
            "subscription_tier_slug": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "do": {
                "interface": do.Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._params = None
        self._name = None
        self._prefix = None

        self._load_params()
        self._create()

    def _load_params(self):
        """TODO"""

        with self.context as ctx:
            self._params = ctx.get_data("parameters", v1.utils.fqcn(self))

            if not self._params:
                self._params = self.parameters
                ctx.set_data("parameters", v1.utils.fqcn(self), self._params)

    def _create(self):
        """TODO"""

        name = f"{self.context.deployment_name}.registry"
        sanitized_name = name.replace(".", "-")

        obj = {
            "kind": "v2/registry",
            "name": name,
            "params": {
                "name": sanitized_name,
                "region": self.interfaces.do.region()
            }
        }

        obj["params"] = v1.utils.merge_dicts(obj["params"], self._params)

        self.interfaces.do.add_object(obj)

        self._name = self.interfaces.do.object_name(obj)
        self._prefix = sanitized_name

    def prefix(self) -> str:
        """TODO"""

        return self._prefix

    def auth(self) -> dict[str, object]:
        """TODO"""

        metadata = self.interfaces.do.object_metadata(self._name)

        return {
            "server": metadata["server"],
            "username": metadata["username"],
            "password": metadata["password"]
        }


class Client(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = container_registry.ClientInterface

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "cr": {
                "interface": Provider,
                "required": True
            }
        }

    def prefix(self) -> str:
        """TODO"""

        return self.interfaces.cr.prefix()

    def auth(self) -> dict[str, object]:
        """TODO"""

        return self.interfaces.cr.auth()


dolib.HANDLERS.update({
    "v2/registry": _V2ContainerRegistry
})

repository = {
    "v1": {
        "providers": [
            Provider
        ],
        "bonds": [
            Client
        ]
    }
}
