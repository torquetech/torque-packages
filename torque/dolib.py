# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import difflib
import functools
import re
import sys
import typing

import requests
import yaml

from torque import v1


class Client:
    """TODO"""

    def __init__(self, endpoint: str, token: str):
        self._endpoint = endpoint
        self._session = requests.Session()

        self._headers = {
            "Authorization": f"Bearer {token}"
        }

    def post(self, path: str, params: object) -> object:
        """TODO"""

        return self._session.post(f"{self._endpoint}/{path}",
                                  headers=self._headers,
                                  json=params)


    def put(self, path: str, params: object) -> object:
        """TODO"""

        return self._session.put(f"{self._endpoint}/{path}",
                                 headers=self._headers,
                                 json=params)

    def get(self, path: str, params=None) -> object:
        """TODO"""

        return self._session.get(f"{self._endpoint}/{path}",
                                 headers=self._headers,
                                 params=params)

    def delete(self, path: str) -> object:
        """TODO"""

        return self._session.delete(f"{self._endpoint}/{path}",
                                    headers=self._headers,
                                    json={})


class V2Certificates:
    """TODO"""

    @classmethod
    def create(cls, client: Client, obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/certificates", obj["params"])
        data = res.json()

        if res.status_code != 201:
            raise RuntimeError(f"{obj['name']}: {data['message']}")

        return {
            "kind": obj["kind"],
            "name": obj["name"],
            "metadata": {
                "id": data["certificate"]["id"]
            },
            "params": obj["params"]
        }

    @classmethod
    def update(cls,
               client: Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise RuntimeError(f"{old_obj['name']}: cannot update certificates")

    @classmethod
    def delete(cls, client: Client, obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/certificates/{obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: Client, obj: dict[str, object]):
        """TODO"""


HANDLERS = {
    "v2/certificates": V2Certificates
}


def connect(endpoint: str, token: str) -> Client:
    """TODO"""

    return Client(endpoint, token)


def _diff(name: str, obj1: dict[str, object], obj2: dict[str, object]):
    """TODO"""

    obj1 = yaml.safe_dump(obj1, sort_keys=False) if obj1 else ""
    obj2 = yaml.safe_dump(obj2, sort_keys=False) if obj2 else ""

    diff = difflib.unified_diff(obj1.split("\n"),
                                obj2.split("\n"),
                                fromfile=f"a/{name}",
                                tofile=f"b/{name}",
                                lineterm="")

    diff = "\n".join(diff)

    return obj1 != obj2, diff


def apply(client: Client,
          current_state: dict[str, object],
          new_state: dict[str, object],
          quiet: bool) -> [typing.Callable]:
    """TODO"""

    wait_hooks = []

    for name, new_obj in new_state.items():
        current_obj = current_state.get(name, None)
        new_obj = v1.utils.resolve_futures(new_obj)

        current_params = None
        new_params = new_obj["params"]

        if current_obj:
            current_params = current_obj["params"]

        changed, diff = _diff(name, current_params, new_params)

        if not changed:
            continue

        if not quiet:
            if not current_obj:
                print(f"creating {name}...", file=sys.stdout)

            else:
                print(f"updating {name}...", file=sys.stdout)

        if not quiet:
            print(diff, file=sys.stdout)

        handler = HANDLERS[new_obj["kind"]]

        if not current_obj:
            new_obj = handler.create(client, new_obj)

        else:
            new_obj = handler.update(client, current_obj, new_obj)

        current_state[name] = new_obj

        wait_hooks.append(functools.partial(handler.wait, client, new_obj))

    for name, current_obj in list(current_state.items()):
        if name in new_state:
            continue

        if not quiet:
            print(f"deleting {name}...", file=sys.stdout)

        _, diff = _diff(name, current_obj["params"], None)

        if not quiet:
            print(diff, file=sys.stdout)

        handler = HANDLERS[current_obj["kind"]]
        handler.delete(client, current_obj)

        current_state.pop(name)

    return wait_hooks
