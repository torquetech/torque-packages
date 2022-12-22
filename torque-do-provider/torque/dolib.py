# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import requests

from torque import v1


class Client:
    """DOCSTRING"""

    def __init__(self, endpoint: str, token: str):
        self._endpoint = endpoint
        self._session = requests.Session()

        self._headers = {
            "Authorization": f"Bearer {token}"
        }

    def post(self, path: str, params: object) -> object:
        """DOCSTRING"""

        return self._session.post(f"{self._endpoint}/{path}",
                                  headers=self._headers,
                                  json=params)

    def put(self, path: str, params: object) -> object:
        """DOCSTRING"""

        return self._session.put(f"{self._endpoint}/{path}",
                                 headers=self._headers,
                                 json=params)

    def get(self, path: str, params=None) -> object:
        """DOCSTRING"""

        return self._session.get(f"{self._endpoint}/{path}",
                                 headers=self._headers,
                                 params=params)

    def delete(self, path: str) -> object:
        """DOCSTRING"""

        return self._session.delete(f"{self._endpoint}/{path}",
                                    headers=self._headers,
                                    json={})


class Resource:
    """DOCSTRING"""

    def __init__(self,
                 client: Client,
                 context: v1.deployment.Context,
                 name: str,
                 object: dict[str, object],
                 quiet: bool):
        self._client = client
        self._name = name
        self._context = context
        self._object = object
        self._quiet = quiet


def connect(endpoint: str, token: str) -> Client:
    """DOCSTRING"""

    return Client(endpoint, token)


HANDLERS = {}
