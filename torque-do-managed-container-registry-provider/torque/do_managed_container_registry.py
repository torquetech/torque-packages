# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import base64

from torque import container_registry
from torque import do
from torque import dolib
from torque import v1


class _V2ContainerRegistry(dolib.Resource):
    """DOCSTRING"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_params = None

    def _get(self) -> bool:
        """DOCSTRING"""

        res = self._client.get("v2/registry")
        data = res.json()

        if res.status_code == 404:
            return False

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        registry = data["registry"]

        self._current_params = {
            "name": registry["name"],
            "region": registry["region"]
        }

        return True

    def _get_tier(self) -> str:
        """DOCSTRING"""

        res = self._client.get("v2/registry/subscription")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        subscription = data["subscription"]

        return subscription["tier"]["slug"]

    def _create(self):
        """DOCSTRING"""

        res = self._client.post("v2/registry", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update_tier(self, tier: str):
        """DOCSTRING"""

        res = self._client.post("v2/registry/subscription", {
            "tier_slug": tier
        })

        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update(self):
        """DOCSTRING"""

        params = self._object["params"]

        if params["name"] != self._current_params["name"]:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify registry name")

        if params["region"] != self._current_params["region"]:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify registry region")

        tier = params["subscription_tier_slug"]
        current_tier = self._get_tier()

        if tier == current_tier:
            return

        self._update_tier(tier)

    def update(self) -> dict[str, object]:
        """DOCSTRING"""

        if not self._get():
            self._create()

        else:
            self._update()

        return self._object | {
            "metadata": {}
        }

    def delete(self):
        """DOCSTRING"""

        with self._context as ctx:
            ctx.delete_secret_data(self._object["name"], "auth")

        if self._object["shared"]:
            return

        res = self._client.delete("v2/registry")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


def _auth(client: dolib.Client, name: str) -> dict[str, str]:
    """DOCSTRING"""

    res = client.get("v2/registry/docker-credentials?read_write=true")
    data = res.json()

    if res.status_code != 200:
        raise v1.exceptions.RuntimeError(f"{name}: {data['message']}")

    data = data["auths"]
    data = list(data.items())

    if len(data) != 1:
        raise v1.exceptions.RuntimeError(f"{name}: invalid response")

    data = data[0]

    server = data[0]
    auth = data[1]["auth"]

    auth = auth.encode()
    auth = base64.b64decode(auth)
    auth = auth.decode()

    n = auth.index(":")

    username = auth[:n]
    password = auth[n+1:]

    return {
        "server": server,
        "username": username,
        "password": password
    }


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

    CONFIGURATION = {
        "defaults": {
            "subscription_tier_slug": "starter",
            "shared": False
        },
        "schema": {
            "subscription_tier_slug": str,
            "shared": bool,
            v1.schema.Optional("name"): str,
            v1.schema.Optional("prefix"): str,
            v1.schema.Optional("region"): str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tier = self.configuration["subscription_tier_slug"]
        self._region = self.configuration.get("region", self.interfaces.do.region())

        prefix = self.configuration.get("prefix")

        if prefix:
            self._name = self.configuration.get("name", self.interfaces.do.project())
            self._prefix = f"{self._name}/{prefix}"

        else:
            self._name = self.configuration.get("name")

            if self._name:
                self._prefix = f"{self._name}/{self.context.deployment_name}"

            else:
                self._name = self.interfaces.do.project()
                self._prefix = self._name

        self._shared = self.configuration["shared"]

        with self.interfaces.do as p:
            p.add_hook("apply-objects", self._apply)

    def _apply(self):
        """DOCSTRING"""

        self.interfaces.do.add_object({
            "kind": "v2/registry",
            "name": self._name,
            "shared": self._shared,
            "params": {
                "name": self._name,
                "region": self._region,
                "subscription_tier_slug": self._tier
            }
        })

    def auth(self) -> dict[str, object]:
        """DOCSTRING"""

        with self.context as ctx:
            auth = ctx.get_secret_data(self._name, "auth")

            if not auth:
                auth = _auth(self.interfaces.do.client(), self._name)
                auth["prefix"] = self._prefix

                ctx.set_secret_data(self._name, "auth", auth)

            return auth


class V1Client(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = container_registry.V1Interface

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "cr": {
                "interface": V1Provider,
                "required": True
            }
        }

    def auth(self) -> dict[str, object]:
        """DOCSTRING"""

        return self.interfaces.cr.auth()


dolib.HANDLERS.update({
    "v2/registry": _V2ContainerRegistry
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1Client
        ]
    }
}
