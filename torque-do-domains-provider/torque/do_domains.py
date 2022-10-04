# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1
from torque import do
from torque import dolib


class _V2Domains:
    """TODO"""

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/domains", new_obj["params"])
        data = res.json()

        if res.status_code not in (201, 422):
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        return new_obj | {
            "metadata": {}
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update domains")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/domains/{old_obj['name']}")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class V1Provider(v1.provider.Provider):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            }
        }

    def create(self, domain: str):
        """TODO"""

        self.interfaces.do.add_object({
            "kind": "v2/domains",
            "name": domain,
            "params": {
                "name": domain
            }
        })

        self.interfaces.do.add_resource("do:domain", domain)


dolib.HANDLERS.update({
    "v2/domains": _V2Domains
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
