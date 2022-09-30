# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import sys
import time
import threading

from torque import v1
from torque import postgres
from torque import do
from torque import dolib


class _V2PostgresClusters:
    """TODO"""

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/databases", new_obj["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["database"]
        conn = data["private_connection"]

        return new_obj | {
            "metadata": {
                "id": data["id"],
                "host": conn["host"],
                "port": conn["port"],
                "ssl": conn["ssl"]
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update database cluster")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/databases/{old_obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""

        cluster_name = obj["name"]
        cluster_id = obj["metadata"]["id"]

        while True:
            res = client.get(f"v2/databases/{cluster_id}")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{cluster_name}: {data['message']}")

            data = data["database"]
            done = data["status"] == "online"

            if done:
                break

            print(f"waiting for cluster {cluster_name} to become ready...",
                  file=sys.stdout)

            time.sleep(10)


class _V2PostgresDatabase:
    """TODO"""

    @classmethod
    def _get_database(cls,
                      client: dolib.Client,
                      cluster_id: str,
                      name: str) -> dict[str, object]:
        """TODO"""

        res = client.get(f"v2/databases/{cluster_id}/dbs")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{name}: {data['message']}")

        for db in data["dbs"]:
            if name == db["name"]:
                return {"db": db}

        raise v1.exceptions.RuntimeError(f"unexpected error while looking for {name}")

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post(f"v2/databases/{new_obj['cluster_id']}/dbs",
                          new_obj["params"])
        data = res.json()

        if res.status_code == 422:
            data = cls._get_database(client, new_obj["cluster_id"], new_obj["params"]["name"])

        elif res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["db"]

        return new_obj | {
            "metadata": {
                "id": new_obj["name"],
                "database": data["name"]
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update database")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class _V2PostgresUser:
    """TODO"""

    @classmethod
    def _get_user(cls,
                  client: dolib.Client,
                  cluster_id: str,
                  name: str) -> dict[str, object]:
        """TODO"""

        res = client.get(f"v2/databases/{cluster_id}/users")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{name}: {data['message']}")

        for user in data["users"]:
            if name == user["name"]:
                return {"user": user}

        raise v1.exceptions.RuntimeError(f"unexpected error while looking for {name}")

    @classmethod
    def create(cls,
               client: dolib.Client,
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post(f"v2/databases/{new_obj['cluster_id']}/users",
                          new_obj["params"])
        data = res.json()

        if res.status_code == 422:
            data = cls._get_user(client, new_obj["cluster_id"], new_obj["params"]["name"])

        elif res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["user"]

        return new_obj | {
            "metadata": {
                "id": new_obj["name"],
                "user": data["name"],
                "password": data["password"]
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update database user")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class Provider(v1.provider.Provider):
    """TODO"""


class Cluster(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = postgres.ClusterInterface

    PARAMETERS = {
        "defaults": {
            "version": "14",
            "num_nodes": 1,
            "size": "db-s-1vcpu-1gb"
        },
        "schema": {
            "version": str,
            "num_nodes": int,
            "size": str,
            v1.schema.Optional("tags"): [str]
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

        self._cluster_id = None
        self._cluster_name = None

        self._databases = {}
        self._users = {}

        self._lock = threading.Lock()

        self._load_params()
        self._create_cluster()

    def _load_params(self):
        """TODO"""

        with self.context as ctx:
            name = f"{v1.utils.fqcn(self)}-{self.name}"
            self._params = ctx.get_data("parameters", name)

            if not self._params:
                self._params = self.parameters
                ctx.set_data("parameters", name, self._params)

    def _show_secret(self, user: str):
        """TODO"""

        user_metadata = self.interfaces.do.object_metadata(self._users[user])

        print(f"{self.name}: user: {user}, password: {user_metadata['password']}")

    def _create_cluster(self):
        """TODO"""

        name = f"{self.context.deployment_name}-{self.name}"
        sanitized_name = name.replace(".", "-")

        obj = {
            "kind": "v2/databases/postgres",
            "name": name,
            "params": {
                "name": sanitized_name,
                "engine": "pg",
                "region": self.interfaces.do.region(),
                "private_network_uuid": self.interfaces.do.vpc_id()
            }
        }

        obj["params"] = v1.utils.merge_dicts(obj["params"], self._params)

        self._cluster_id = self.interfaces.do.add_object(obj)
        self._cluster_name = self.interfaces.do.object_name(obj)

        self.interfaces.do.add_resource("do:dbaas", self._cluster_id)

    def _create_database(self, name: str):
        """TODO"""

        with self._lock:
            if name in self._databases:
                return

            obj = {
                "kind": "v2/databases/postgres/db",
                "name": f"{self.name}-database-{name}",
                "cluster_id": self._cluster_id,
                "params": {
                    "name": name
                }
            }

            self.interfaces.do.add_object(obj)
            self._databases[name] = self.interfaces.do.object_name(obj)

    def _create_user(self, name: str):
        """TODO"""

        with self._lock:
            if name in self._users:
                return

            with self.context as ctx:
                ctx.add_hook("show-secrets", functools.partial(self._show_secret,
                                                               name))

            obj = {
                "kind": "v2/databases/postgres/user",
                "name": f"{self.name}-user-{name}",
                "cluster_id": self._cluster_id,
                "params": {
                    "name": name
                }
            }

            self.interfaces.do.add_object(obj)
            self._users[name] = self.interfaces.do.object_name(obj)

    def _resolve_uri(self, database: str, user: str) -> str:
        """TODO"""

        user_metadata = self.interfaces.do.object_metadata(self._users[user])
        db_metadata = self.interfaces.do.object_metadata(self._databases[database])
        cluster_metadata = self.interfaces.do.object_metadata(self._cluster_name)

        user = user_metadata["user"]
        password = user_metadata["password"]
        database = db_metadata["database"]
        host = cluster_metadata["host"]
        port = cluster_metadata["port"]

        return f"postgres://{user}:{password}@{host}:{port}/{database}"

    def uri(self, database: str, user: str) -> v1.utils.Future[str]:
        """TODO"""

        self._create_database(database)
        self._create_user(user)

        return v1.utils.Future(functools.partial(self._resolve_uri, database, user))


dolib.HANDLERS.update({
    "v2/databases/postgres": _V2PostgresClusters,
    "v2/databases/postgres/db": _V2PostgresDatabase,
    "v2/databases/postgres/user": _V2PostgresUser
})

repository = {
    "v1": {
        "providers": [
            Provider
        ],
        "bonds": [
            Cluster
        ]
    }
}
