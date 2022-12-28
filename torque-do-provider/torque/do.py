# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import io
import os

import boto3
import yaml

from torque import dolib
from torque import v1


class _V2Project(dolib.Resource):
    """DOCSTRING"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._do_name = self._object["name"]

        self._current_params = None
        self._project_id = None

        if "metadata" in self._object:
            self._project_id = self._object["metadata"]["id"]

    def _get(self) -> bool:
        """DOCSTRING"""

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
        """DOCSTRING"""

        res = self._client.post("v2/projects", self._object["params"])
        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._project_id = data["project"]["id"]

    def _update(self):
        """DOCSTRING"""

        if self._object["params"] == self._current_params:
            return

        params = {} | self._object["params"]
        params["is_default"] = False

        res = self._client.put(f"v2/projects/{self._project_id}", params)
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def update(self) -> dict[str, object]:
        """DOCSTRING"""

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
        """DOCSTRING"""

        res = self._client.delete(f"v2/projects/{self._project_id}")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


class _V2Vpc(dolib.Resource):
    """DOCSTRING"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._do_name = self._object["name"]
        self._region = self._object["params"]["region"]

        self._current_params = None
        self._vpc_id = None

        self._has_default_vpc = False

        if "metadata" in self._object:
            self._vpc_id = self._object["metadata"]["id"]

    def _get(self) -> bool:
        """DOCSTRING"""

        res = self._client.get("v2/vpcs")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        for vpc in data["vpcs"]:
            if vpc["default"] and vpc["region"] == self._region:
                self._has_default_vpc = True

            if self._do_name == vpc["name"]:
                self._current_params = {
                    "name": vpc["name"],
                    "region": vpc["region"]
                }

                self._vpc_id = vpc["id"]

        return self._vpc_id is not None

    def _create_default_vpc(self):
        """DOCSTRING"""

        default_vpc = f"{self._region}-vpc-default"

        res = self._client.post("v2/vpcs", {
            "name": default_vpc,
            "region": self._region,
            "default": True
        })

        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{default_vpc}: {data['message']}")

    def _create(self):
        """DOCSTRING"""

        if not self._has_default_vpc:
            self._create_default_vpc()

        res = self._client.post("v2/vpcs", self._object["params"])
        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._vpc_id = data["vpc"]["id"]

    def _update(self):
        """DOCSTRING"""

        current_region = self._current_params["region"]
        new_region = self._object["params"]["region"]

        if current_region != new_region:
            raise v1.exceptions.RuntimeError(f"{self._name}: cannot change region")

    def update(self) -> dict[str, object]:
        """DOCSTRING"""

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
        """DOCSTRING"""

        def cond():
            res = self._client.delete(f"v2/vpcs/{self._vpc_id}")

            if res.status_code == 204:
                return True

            if res.status_code != 403:
                raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")

            return False

        v1.utils.wait_for(cond, f"waiting for {self._name} resources to be deleted")


class _V2Resources(dolib.Resource):
    """DOCSTRING"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_params = None
        self._project_id = None

        if "params" in self._object:
            self._project_id = self._object["params"]["project_id"]

    def _get(self) -> bool:
        """DOCSTRING"""

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
        """DOCSTRING"""

        if not params["resources"]:
            return

        res = self._client.post(f"v2/projects/{self._project_id}/resources", params)
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _create(self):
        """DOCSTRING"""

        self._assign(self._object["params"])

    def _update(self):
        """DOCSTRING"""

        params = {
            "resources": sorted(self._object["params"]["resources"])
        }

        if params == self._current_params:
            return

        self._assign(params)

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


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

    CONFIGURATION = {
        "defaults": {
            "endpoint": "https://api.digitalocean.com",
            "region": "nyc3",
            "quiet": True
        },
        "schema": {
            "endpoint": str,
            "region": str,
            "quiet": bool,
            v1.schema.Optional("overrides"): dict
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._region = self.configuration["region"]

        self._project = self.context.deployment_name
        self._vpc = self.context.deployment_name

        self._client = None

        self._current_state = {}
        self._new_state = {}
        self._resources = []

        self._load_state()

        with self as p:
            p.add_hook("apply-objects", self._apply_project)
            p.add_hook("apply-objects", self._apply_vpc)
            p.add_hook("apply", self._apply)
            p.add_hook("delete", self._delete)

    def _load_state(self):
        """DOCSTRING"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", v1.utils.fqcn(self)) or {}

    def _store_state(self):
        """DOCSTRING"""

        with self.context as ctx:
            ctx.set_data("state", v1.utils.fqcn(self), self._current_state)

    def _connect(self) -> dolib.Client:
        """DOCSTRING"""

        self._client = dolib.connect(self.configuration["endpoint"], self.token())

    def _update_object(self, name: str):
        """DOCSTRING"""

        overrides = self.configuration.get("overrides", {})
        overrides = overrides.get(name, {})

        old_obj = self._current_state.get(name)

        obj = v1.utils.resolve_futures(self._new_state.get(name))
        obj = v1.utils.merge_dicts(obj, overrides)

        if old_obj:
            old_obj = {} | old_obj
            old_obj.pop("metadata", None)

        if old_obj == obj:
            return

        if not self.configuration["quiet"]:
            print(v1.utils.diff_objects(name, old_obj, obj))

        handler = dolib.HANDLERS[obj["kind"]](self._client,
                                              self.context,
                                              name,
                                              obj,
                                              self.configuration["quiet"])

        self._current_state[name] = handler.update()

    def _delete_object(self, name: str):
        """DOCSTRING"""

        obj = self._current_state.get(name)

        handler = dolib.HANDLERS[obj["kind"]](self._client,
                                              self.context,
                                              name,
                                              obj,
                                              self.configuration["quiet"])

        def _delete_object():
            if not self.configuration["quiet"]:
                print(v1.utils.diff_objects(name, obj, {}))

            handler.delete()
            self._current_state.pop(name)

        with self as p:
            p.add_hook("collect-garbage", _delete_object)

    def _apply_project(self):
        """DOCSTRING"""

        self.add_object({
            "kind": "v2/project",
            "name": self._project,
            "params": {
                "name": self._project,
                "description": "torquetech.io deployment",
                "purpose": "Other: Torque deployment",
                "environment": "Production"
            }
        })

    def _apply_vpc(self):
        """DOCSTRING"""

        self.add_object({
            "kind": "v2/vpc",
            "name": self._vpc,
            "params": {
                "name": self._vpc,
                "region": self._region
            }
        })

    def _apply(self):
        """DOCSTRING"""

        self.add_object({
            "kind": "v2/resources",
            "name": self._project,
            "params": {
                "project_id": self.project_id(),
                "resources": self._resources
            }
        })

        try:
            self._connect()

            v1.utils.apply_objects(self._current_state,
                                   self._new_state,
                                   self._update_object,
                                   self._delete_object)

        finally:
            self._store_state()

    def _delete(self):
        """DOCSTRING"""

        try:
            self._connect()

            v1.utils.apply_objects(self._current_state,
                                   {},
                                   self._update_object,
                                   self._delete_object)

        finally:
            self._store_state()

    def metadata(self, name: str) -> dict[str, object]:
        """DOCSTRING"""

        return self._current_state[name]["metadata"]

    def object_id(self, name: str) -> v1.utils.Future[str]:
        """DOCSTRING"""

        return v1.utils.Future(lambda: self.metadata(name)["id"])

    def project_id(self) -> v1.utils.Future[str]:
        """DOCSTRING"""

        return self.object_id(f"v2/project/{self._project}")

    def vpc_id(self) -> v1.utils.Future[str]:
        """DOCSTRING"""

        return self.object_id(f"v2/vpc/{self._vpc}")

    def project(self) -> str:
        """DOCSTRING"""

        return self._project

    def region(self) -> str:
        """DOCSTRING"""

        return self._region

    def token(self) -> str:
        """DOCSTRING"""

        token = os.getenv("DO_TOKEN")

        if not token:
            raise v1.exceptions.RuntimeError("DO_TOKEN environment not set")

        return token

    def client(self) -> dolib.Client:
        """DOCSTRING"""

        return self._client

    def add_resource(self, type: str, resource_id: object):
        """DOCSTRING"""

        resource = v1.utils.Future(lambda: f"{type}:{v1.utils.resolve_futures(resource_id)}")

        with self._lock:
            self._resources.append(resource)

    def add_object(self, obj: dict[str, object]) -> str:
        """DOCSTRING"""

        with self._lock:
            name = f"{obj['kind']}/{obj['name']}"

            if name in self._new_state:
                raise v1.exceptions.RuntimeError(f"{name}: digitalocean object already exists")

            self._new_state[name] = obj

            return name

    def object(self, name: str) -> dict[str, object]:
        """DOCSTRING"""

        if name not in self._new_state:
            raise v1.exceptions.RuntimeError(f"{name}: object not found")

        return self._new_state[name]

    def objects(self) -> dict[str, object]:
        """DOCSTRING"""

        return self._new_state


class V1Context(v1.deployment.Context):
    """DOCSTRING"""

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
        """DOCSTRING"""

        key = f"{self.configuration['path']}/{key}"

        try:
            res = self._client.get_object(Bucket=self.configuration["bucket"],
                                          Key=key)

            return res["Body"]

        except self._client.exceptions.NoSuchKey:
            return io.BytesIO(b"")

    def _put_s3_key(self, key: str, body: bytes):
        """DOCSTRING"""

        key = f"{self.configuration['path']}/{key}"

        self._client.put_object(Bucket=self.configuration["bucket"],
                                Key=key,
                                Body=body,
                                ACL='private')

    def load_bucket(self, name: str) -> dict[str, object]:
        """DOCSTRING"""

        key = f"{self.deployment_name}/{name}.yaml"

        return yaml.safe_load(self._get_s3_key(key)) or {}

    def store_bucket(self, name: str, data: dict[str, object]):
        """DOCSTRING"""

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
