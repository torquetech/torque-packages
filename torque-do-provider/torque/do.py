# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import os

from torque import v1
from torque import dolib


class _V2Projects:
    """TODO"""

    @classmethod
    def _get_project(cls,
                     client: dolib.Client,
                     name: str) -> dict[str, object]:
        """TODO"""

        res = client.get("v2/projects")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{name}: {data['message']}")

        for project in data["projects"]:
            if name == project["name"]:
                return project

        raise v1.exceptions.RuntimeError(f"unexpected error while looking for {name}")

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/projects", new_obj["params"])
        data = res.json()

        if res.status_code != 201:
            if res.status_code != 409:
                raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

            data = cls._get_project(client, new_obj["name"])

        else:
            data = data["project"]

        return new_obj | {
            "metadata": {
                "id": data["id"]
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update projects")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/projects/{old_obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class _V2Vpcs:
    """TODO"""

    @classmethod
    def _get_vpc(cls,
                 client: dolib.Client,
                 name: str) -> dict[str, object]:
        """TODO"""

        res = client.get("v2/vpcs")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{name}: {data['message']}")

        for vpc in data["vpcs"]:
            if name == vpc["name"]:
                return vpc

        raise v1.exceptions.RuntimeError(f"unexpected error while looking for {name}")

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/vpcs", new_obj["params"])
        data = res.json()

        if res.status_code != 201:
            if res.status_code != 422:
                raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

            data = cls._get_vpc(client, new_obj["name"])

        else:
            data = data["vpc"]

        return new_obj | {
            "metadata": {
                "id": data["id"]
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update vpcs")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/vpcs/{old_obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class _V2Resources:
    """TODO"""

    @classmethod
    def _assign(cls,
                client: dolib.Client,
                project_name: str,
                project_id: str,
                resources: [str]):
        """TODO"""

        if not resources:
            return

        res = client.post(f"v2/projects/{project_id}/resources", {
            "resources": resources
        })

        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{project_name}: {data['message']}")

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        params = new_obj["params"]
        project_name = new_obj["name"]

        project_id = params["project_id"]
        resources = params["resources"]

        cls._assign(client, project_name, project_id, resources)

        return new_obj | {
            "metadata": {}
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        # pylint: disable=W0613

        """TODO"""

        params = new_obj["params"]
        project_name = new_obj["name"]

        project_id = params["project_id"]
        resources = params["resources"]

        cls._assign(client, project_name, project_id, resources)

        return new_obj | {
            "metadata": {}
        }

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class Provider(v1.provider.Provider):
    """TODO"""

    _PARAMETERS = {
        "defaults": {
            "endpoint": "https://api.digitalocean.com",
            "region": "nyc3"
        },
        "schema": {
            "endpoint": str,
            "region": str
        }
    }

    _CONFIGURATION = {
        "defaults": {
            "quiet": True
        },
        "schema": {
            "quiet": bool
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._params = None
        self._client = None

        self._current_state = {}
        self._new_state = {}
        self._resources = []

        self._load_params()
        self._load_state()

        self._connect()

        self.add_object({
            "kind": "v2/projects",
            "name": self._params["project_name"],
            "params": {
                "name": self._params["project_name"],
                "purpose": "torquetech.io deployment",
                "environment": "Production"
            }
        })

        self.add_object({
            "kind": "v2/vpcs",
            "name": self._params["vpc_name"],
            "params": {
                "name": self._params["vpc_name"],
                "region": self._params["region"]
            }
        })

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

    def _load_params(self):
        """TODO"""

        with self.context as ctx:
            self._params = ctx.get_data("parameters", v1.utils.fqcn(self))

            if not self._params:
                project_name = self.context.deployment_name
                vpc_name = f"{project_name}-{self.parameters['region']}"

                self._params = {
                    "endpoint": self.parameters["endpoint"],
                    "region": self.parameters["region"],
                    "project_name": project_name,
                    "vpc_name": vpc_name
                }

                ctx.set_data("parameters", v1.utils.fqcn(self), self._params)

    def _load_state(self) -> dict[str, object]:
        """TODO"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", v1.utils.fqcn(self)) or {}

    def _store_state(self):
        """TODO"""

        with self.context as ctx:
            ctx.set_data("state", v1.utils.fqcn(self), self._current_state)

    def _connect(self) -> dolib.Client:
        """TODO"""

        self._client = dolib.connect(self._params["endpoint"], self.token())

    def _apply(self):
        """TODO"""

        self.add_object({
            "kind": "v2/resources",
            "name": self._params["project_name"],
            "params": {
                "project_id": self.project_id(),
                "resources": self._resources
            }
        })

        try:
            dolib.apply(self._client,
                        self._current_state,
                        self._new_state,
                        self.configuration["quiet"])

        finally:
            self._store_state()

    def _delete(self):
        """TODO"""

        try:
            dolib.apply(self._client,
                        self._current_state,
                        {},
                        self.configuration["quiet"])

        finally:
            self._store_state()

    def _resolve_resource(self, type: str, resource_id: object):
        """TODO"""

        return f"{type}:{v1.utils.resolve_futures(resource_id)}"

    def _resolve_object_metadata(self, name: str) -> dict[str, object]:
        """TODO"""

        if name not in self._current_state:
            raise v1.exceptions.RuntimeError(f"{name}: object not found")

        return self._current_state[name]["metadata"]

    def _resolve_object_id(self, name: str) -> str:
        """TODO"""

        return self._resolve_object_metadata(name)["id"]

    def _object_id(self, name: str) -> v1.utils.Future[str]:
        """TODO"""

        return v1.utils.Future(functools.partial(self._resolve_object_id, name))

    def project_id(self) -> v1.utils.Future[str]:
        """TODO"""

        return self._object_id(f"v2/projects/{self._params['project_name']}")

    def vpc_id(self) -> v1.utils.Future[str]:
        """TODO"""

        return self._object_id(f"v2/vpcs/{self._params['vpc_name']}")

    def region(self) -> str:
        """TODO"""

        return self._params["region"]

    def token(self) -> str:
        """TODO"""

        return os.getenv("DO_TOKEN")

    def client(self) -> dolib.Client:
        """TODO"""

        return self._client

    def object_name(self, obj: dict[str, object]) -> str:
        """TODO"""

        return f"{obj['kind']}/{obj['name']}"

    def object_metadata(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._resolve_object_metadata(name)

    def add_object(self, obj: dict[str, object]):
        """TODO"""

        with self._lock:
            name = self.object_name(obj)

            if name in self._new_state:
                raise v1.exceptions.RuntimeError(f"{name}: digitalocean object already exists")

            self._new_state[name] = obj

            return self._object_id(name)

    def add_resource(self, type: str, resource_id: object):
        """TODO"""

        with self._lock:
            resource = v1.utils.Future(functools.partial(self._resolve_resource,
                                                         type,
                                                         resource_id))
            self._resources.append(resource)


dolib.HANDLERS.update({
    "v2/projects": _V2Projects,
    "v2/vpcs": _V2Vpcs,
    "v2/resources": _V2Resources
})

repository = {
    "v1": {
        "providers": [
            Provider
        ]
    }
}
