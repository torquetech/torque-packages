# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import do
from torque import dolib
from torque import v1


class _V2Domain(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._do_name = self._object["name"]

        self._current_params = None

    def _get(self) -> bool:
        """TODO"""

        page = 1

        while True:
            res = self._client.get(f"v2/domains?page={page}&per_page=20")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

            domains = data["domains"]

            for domain in domains:
                if self._do_name == domain["name"]:
                    self._current_params = {
                        "name": domain["name"]
                    }

                    return True

            if len(domains) != 20:
                break

            page += 1

        return False

    def _create(self):
        """TODO"""

        res = self._client.post("v2/domains", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update(self):
        """TODO"""

        if self._object["params"] == self._current_params:
            return

        raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify domain")

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

        res = self._client.delete(f"v2/domains/{self._do_name}")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


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
            "kind": "v2/domain",
            "name": domain,
            "params": {
                "name": domain
            }
        })

        self.interfaces.do.add_resource("do:domain", domain)


dolib.HANDLERS.update({
    "v2/domain": _V2Domain
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
