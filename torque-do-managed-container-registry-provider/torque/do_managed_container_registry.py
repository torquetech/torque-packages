# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import base64

from torque import container_registry
from torque import do
from torque import dolib
from torque import v1


class _V2ContainerRegistry(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_params = None

    def _get(self) -> bool:
        """TODO"""

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
        """TODO"""

        res = self._client.get("v2/registry/subscription")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        subscription = data["subscription"]

        return subscription["tier"]["slug"]

    def _create(self):
        """TODO"""

        res = self._client.post("v2/registry", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update_tier(self, tier: str):
        """TODO"""

        res = self._client.post("v2/registry/subscription", {
            "tier_slug": tier
        })

        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update(self):
        """TODO"""

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
        """TODO"""

        if not self._get():
            self._create()

        else:
            self._update()

        return self._object | {
            "metadata": {}
        }

    def delete(self):
        """TODO"""

        with self._context as ctx:
            ctx.delete_secret_data(self._object["name"], "auth")

        res = self._client.delete("v2/registry")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


def _auth(client: dolib.Client, name: str) -> dict[str, str]:
    """TODO"""

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
    """TODO"""

    CONFIGURATION = {
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
                "interface": do.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._name = f"{self.context.deployment_name}-registry"

        with self.interfaces.do as p:
            p.add_hook("apply-objects", self._apply)

    def _apply(self):
        """TODO"""

        obj = {
            "kind": "v2/registry",
            "name": self._name,
            "params": {
                "name": self._name,
                "region": self.interfaces.do.region()
            }
        }

        obj["params"] = v1.utils.merge_dicts(obj["params"], self.configuration)

        self.interfaces.do.add_object(obj)

    def auth(self) -> dict[str, object]:
        """TODO"""

        with self.context as ctx:
            auth = ctx.get_secret_data(self._name, "auth")

            if not auth:
                auth = _auth(self.interfaces.do.client(), self._name)
                auth["prefix"] = self._name

                ctx.set_secret_data(self._name, "auth", auth)

            return auth


class V1Client(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = container_registry.V1Interface

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "cr": {
                "interface": V1Provider,
                "required": True
            }
        }

    def auth(self) -> dict[str, object]:
        """TODO"""

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
