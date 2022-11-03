# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import io
import os
import sys
import time

import boto3
import yaml

from torque import dolib
from torque import v1


class _V2Project(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._do_name = self._object["name"]

        self._current_params = None
        self._project_id = None

        if "metadata" in self._object:
            self._project_id = self._object["metadata"]["id"]

    def _get(self) -> bool:
        """TODO"""

        res = self._client.get("v2/projects")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        for project in data["projects"]:
            if self._do_name == project["name"]:
                self._current_params = {
                    "name": project["name"],
                    "description": project["description"],
                    "purpose": project["purpose"],
                    "environment": project["environment"]
                }

                self._project_id = project["id"]

                return True

        return False

    def _create(self):
        """TODO"""

        res = self._client.post("v2/projects", self._object["params"])
        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._project_id = data["project"]["id"]

    def _update(self):
        """TODO"""

        if self._object["params"] == self._current_params:
            return

        params = {} | self._object["params"]
        params["is_default"] = False

        res = self._client.put(f"v2/projects/{self._project_id}", params)
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def update(self) -> dict[str, object]:
        """TODO"""

        if not self._get():
            self._create()

        else:
            self._update()

        return self._object | {
            "metadata": {
                "id": self._project_id
            }
        }

    def delete(self):
        """TODO"""

        res = self._client.delete(f"v2/projects/{self._project_id}")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


class _V2Vpc(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._do_name = self._object["name"]

        self._current_params = None
        self._vpc_id = None

        if "metadata" in self._object:
            self._vpc_id = self._object["metadata"]["id"]

    def _get(self) -> bool:
        """TODO"""

        res = self._client.get("v2/vpcs")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        for vpc in data["vpcs"]:
            if self._do_name == vpc["name"]:
                self._current_params = {
                    "name": vpc["name"],
                    "region": vpc["region"]
                }

                self._vpc_id = vpc["id"]

                return True

        return False

    def _create(self):
        """TODO"""

        res = self._client.post("v2/vpcs", self._object["params"])
        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._vpc_id = data["vpc"]["id"]

    def _update(self):
        """TODO"""

        current_region = self._current_params["region"]
        new_region = self._object["params"]["region"]

        if current_region != new_region:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot change region")

    def update(self) -> dict[str, object]:
        """TODO"""

        if not self._get():
            self._create()

        else:
            self._update()

        return self._object | {
            "metadata": {
                "id": self._vpc_id
            }
        }

    def delete(self):
        """TODO"""

        i = 0

        while True:
            res = self._client.delete(f"v2/vpcs/{self._vpc_id}")

            if res.status_code == 204:
                break

            if res.status_code != 403:
                raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")

            if i == 0:
                print(f"waiting for {self._name} resources to be deleted",
                      file=sys.stdout, end="")

                i = 1

            if i != 4:
                print(".", end="")
                i += 1

            else:
                print("\x08\x08\x08   \x08\x08\x08", file=sys.stdout, end="")
                i = 1

            sys.stdout.flush()

            time.sleep(1)

        if i != 0:
            print("." * (4 - i), file=sys.stdout)


class _V2Resources(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_params = None
        self._project_id = None

        if "params" in self._object:
            self._project_id = self._object["params"]["project_id"]

    def _get(self) -> bool:
        """TODO"""

        res = self._client.get(f"v2/projects/{self._project_id}/resources")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._current_params = {
            "resources": sorted([
                resource["urn"] for resource in data["resources"]
            ])
        }

    def _assign(self, params: dict[str, object]):
        """TODO"""

        if not params["resources"]:
            return

        res = self._client.post(f"v2/projects/{self._project_id}/resources", params)
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _create(self):
        """TODO"""

        self._assign(self._object["params"])

    def _update(self):
        """TODO"""

        params = {
            "resources": sorted(self._object["params"]["resources"])
        }

        if params == self._current_params:
            return

        self._assign(params)

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


class V1Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "endpoint": "https://api.digitalocean.com",
            "region": "nyc3",
            "quiet": True
        },
        "schema": {
            "endpoint": str,
            "region": str,
            "quiet": bool
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._region = self.configuration["region"]

        self._project_name = self.context.deployment_name
        self._vpc_name = self.context.deployment_name

        self._client = None

        self._current_state = {}
        self._new_state = {}
        self._resources = []

        self._load_state()

        self._connect()

        self.add_object({
            "kind": "v2/project",
            "name": self._project_name,
            "params": {
                "name": self._project_name,
                "description": "torquetech.io deployment",
                "purpose": "Other: Torque deployment",
                "environment": "Production"
            }
        })

        self.add_object({
            "kind": "v2/vpc",
            "name": self._vpc_name,
            "params": {
                "name": self._vpc_name,
                "region": self._region
            }
        })

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

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

        self._client = dolib.connect(self.configuration["endpoint"], self.token())

    def _update_object(self, name: str):
        """TODO"""

        old_obj = self._current_state.get(name)
        obj = v1.utils.resolve_futures(self._new_state.get(name))

        if old_obj:
            old_obj = {} | old_obj
            old_obj.pop("metadata", None)

        if old_obj == obj:
            return

        if not self.configuration["quiet"]:
            diff = v1.utils.diff_objects(name, old_obj, obj)
            print(diff, file=sys.stdout)

        handler = dolib.HANDLERS[obj["kind"]](self._client,
                                              self.context,
                                              name,
                                              obj,
                                              self.configuration["quiet"])

        self._current_state[name] = handler.update()

    def _delete_object(self, name: str):
        """TODO"""

        obj = self._current_state.get(name)

        handler = dolib.HANDLERS[obj["kind"]](self._client,
                                              self.context,
                                              name,
                                              obj,
                                              self.configuration["quiet"])

        def _delete_object():
            if not self.configuration["quiet"]:
                diff = v1.utils.diff_objects(name, obj, {})
                print(diff, file=sys.stdout)

            handler.delete()
            self._current_state.pop(name)

        with self.context as ctx:
            ctx.add_hook("gc", _delete_object)

    def _apply(self):
        """TODO"""

        self.add_object({
            "kind": "v2/resources",
            "name": self._project_name,
            "params": {
                "project_id": self.project_id(),
                "resources": self._resources
            }
        })

        try:
            v1.utils.apply_objects(self._current_state,
                                   self._new_state,
                                   self._update_object,
                                   self._delete_object)

        finally:
            self._store_state()

    def _delete(self):
        """TODO"""

        try:
            v1.utils.apply_objects(self._current_state,
                                   {},
                                   self._update_object,
                                   self._delete_object)

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

        return self._object_id(f"v2/project/{self._project_name}")

    def vpc_id(self) -> v1.utils.Future[str]:
        """TODO"""

        return self._object_id(f"v2/vpc/{self._vpc_name}")

    def region(self) -> str:
        """TODO"""

        return self._region

    def token(self) -> str:
        """TODO"""

        token = os.getenv("DO_TOKEN")

        if not token:
            raise v1.exceptions.RuntimeError("DO_TOKEN environment not set")

        return token

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


class V1Context(v1.deployment.Context):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "region": "nyc3",
            "bucket": "unique-spaces-bucket",
            "path": "deployments"
        },
        "schema": {
            "region": str,
            "bucket": str,
            "path": str,
            v1.schema.Optional("endpoint"): str
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._key = os.getenv("DO_SPACES_KEY")
        self._secret = os.getenv("DO_SPACES_SECRET")

        if not self._key:
            raise v1.exceptions.RuntimeError("DO_SPACES_KEY environment not set")

        if not self._secret:
            raise v1.exceptions.RuntimeError("DO_SPACES_SECRET environment not set")

        endpoint = self.configuration.get("endpoint", "digitaloceanspaces.com")
        self._endpoint_url = f"https://{self.configuration['region']}.{endpoint}"

        self._session = boto3.session.Session()

        self._client = self._session.client("s3",
                                            endpoint_url=self._endpoint_url,
                                            region_name=self.configuration["region"],
                                            aws_access_key_id=self._key,
                                            aws_secret_access_key=self._secret)

        try:
            self._client.create_bucket(Bucket=self.configuration["bucket"])

        except self._client.exceptions.BucketAlreadyExists:
            pass

    def _get_s3_key(self, key: str) -> object:
        """TODO"""

        key = f"{self.configuration['path']}/{key}"

        try:
            res = self._client.get_object(Bucket=self.configuration["bucket"],
                                          Key=key)

            return res["Body"]

        except self._client.exceptions.NoSuchKey:
            return io.BytesIO(b"")

    def _put_s3_key(self, key: str, body: bytes):
        """TODO"""

        key = f"{self.configuration['path']}/{key}"

        self._client.put_object(Bucket=self.configuration["bucket"],
                                Key=key,
                                Body=body,
                                ACL='private')

    def load_bucket(self, name: str) -> dict[str, object]:
        """TODO"""

        key = f"{self.deployment_name}/{name}.yaml"

        return yaml.safe_load(self._get_s3_key(key)) or {}

    def store_bucket(self, name: str, data: dict[str, object]):
        """TODO"""

        data = yaml.safe_dump(data,
                              default_flow_style=False,
                              sort_keys=False)

        self._put_s3_key(f"{self.deployment_name}/{name}.yaml", data)


dolib.HANDLERS.update({
    "v2/project": _V2Project,
    "v2/vpc": _V2Vpc,
    "v2/resources": _V2Resources
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "contexts": [
            V1Context
        ]
    }
}
