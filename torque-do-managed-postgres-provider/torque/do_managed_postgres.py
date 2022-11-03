# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import threading

from torque import do
from torque import dolib
from torque import postgres
from torque import v1


class _V2PostgresCluster(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_params = None
        self._cluster_name = self._object["cluster_name"]

        self._host = None
        self._port = None
        self._ssl = None

        self._cluster_id = None

        if "metadata" in self._object:
            self._cluster_id = self._object["metadata"]["id"]

    def _get(self) -> bool:
        """TODO"""

        res = self._client.get("v2/databases")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        databases = data["databases"]

        for database in databases:
            if self._cluster_name == database["name"]:
                self._current_params = {
                    "name": database["name"],
                    "engine": database["engine"],
                    "region": database["region"],
                    "private_network_uuid": database["private_network_uuid"],
                    "version": database["version"],
                    "num_nodes": database["num_nodes"],
                    "size": database["size"]
                }

                self._cluster_id = database["id"]

                conn = database["private_connection"]

                self._host = conn["host"]
                self._port = conn["port"]
                self._ssl = conn["ssl"]

                return True

        return False

    def _create(self):
        """TODO"""

        res = self._client.post("v2/databases", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        database = data["database"]

        self._cluster_id = database["id"]

        conn = database["private_connection"]

        self._host = conn["host"]
        self._port = conn["port"]
        self._ssl = conn["ssl"]

    def _update(self):
        """TODO"""

        if self._object["params"] == self._current_params:
            return

        raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify database")

    def _wait(self):
        """TODO"""

        def cond():
            res = self._client.get(f"v2/databases/{self._cluster_id}")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

            database = data["database"]
            done = database["status"] == "online"

            return done

        v1.utils.wait_for(cond, f"waiting for cluster {self._name} to become ready")

    def update(self) -> dict[str, object]:
        """TODO"""

        if not self._get():
            self._create()

        else:
            self._update()

        self._wait()

        return self._object | {
            "metadata": {
                "id": self._cluster_id,
                "host": self._host,
                "port": self._port,
                "ssl": self._ssl
            }
        }

    def delete(self):
        """TODO"""

        res = self._client.delete(f"v2/databases/{self._cluster_id}")

        if res.status_code != 204:
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


class _V2PostgresDatabase(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cluster_id = self._object["cluster_id"]
        self._db_name = self._object["db_name"]

    def _get(self):
        """TODO"""

        res = self._client.get(f"v2/databases/{self._cluster_id}/dbs")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        for db in data["dbs"]:
            if self._db_name == db["name"]:
                return True

        return False

    def _create(self):
        """TODO"""

        res = self._client.post(f"v2/databases/{self._cluster_id}/dbs", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

    def _update(self):
        """TODO"""

    def update(self):
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

        res = self._client.delete(f"v2/databases/{self._cluster_id}/dbs/{self._db_name}")

        if res.status_code not in (204, 412):
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


class _V2PostgresUser(dolib.Resource):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cluster_id = self._object["cluster_id"]
        self._user_name = self._object["user"]

    def _get(self):
        """TODO"""

        res = self._client.get(f"v2/databases/{self._cluster_id}/users")
        data = res.json()

        if res.status_code != 200:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        for user in data["users"]:
            if self._user_name == user["name"]:
                with self._context as ctx:
                    ctx.set_secret_data(self._object["name"],
                                        "password",
                                        user["password"])

                return True

        return False

    def _create(self):
        """TODO"""

        res = self._client.post(f"v2/databases/{self._cluster_id}/users", self._object["params"])
        data = res.json()

        if res.status_code != 201:
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        user = data["user"]

        with self._context as ctx:
            ctx.set_secret_data(self._object["name"],
                                "password",
                                user["password"])

    def _update(self):
        """TODO"""

    def update(self):
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
            ctx.delete_secret_data(self._object["name"], "password")

        res = self._client.delete(f"v2/databases/{self._cluster_id}/users/{self._user_name}")

        if res.status_code not in (204, 412):
            raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1Cluster(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = postgres.V1ClusterInterface

    CONFIGURATION = {
        "defaults": {
            "version": "14",
            "num_nodes": 1,
            "size": "db-s-1vcpu-1gb"
        },
        "schema": {
            "version": str,
            "num_nodes": int,
            "size": str
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

        self._cluster_id = None
        self._cluster_name = None

        self._databases = {}
        self._users = {}

        self._lock = threading.Lock()

        self._create_cluster()

    def _show_secret(self, user: str):
        """TODO"""

        with self.context as ctx:
            password = ctx.get_secret_data(self._users[user], "password")

        print(f"{self.name}: user: {user}, password: {password}")

    def _create_cluster(self):
        """TODO"""

        name = f"{self.context.deployment_name}-{self.name}"
        sanitized_name = name.replace(".", "-")

        obj = {
            "kind": "v2/database/postgres",
            "name": name,
            "owner": self.name,
            "cluster_name": sanitized_name,
            "params": {
                "name": sanitized_name,
                "engine": "pg",
                "region": self.interfaces.do.region(),
                "private_network_uuid": self.interfaces.do.vpc_id()
            }
        }

        obj["params"] = v1.utils.merge_dicts(obj["params"], self.configuration)

        self._cluster_id = self.interfaces.do.add_object(obj)
        self._cluster_name = self.interfaces.do.object_name(obj)

        self.interfaces.do.add_resource("do:dbaas", self._cluster_id)

    def _create_database(self, name: str):
        """TODO"""

        if name in self._databases:
            return

        obj = {
            "kind": "v2/database/postgres/db",
            "name": f"{self.name}-database-{name}",
            "owner": self.name,
            "depends_on": self._cluster_name,
            "cluster_id": self._cluster_id,
            "db_name": name,
            "params": {
                "name": name
            }
        }

        self.interfaces.do.add_object(obj)
        self._databases[name] = f"{self.name}-database-{name}"

    def _create_user(self, name: str):
        """TODO"""

        if name in self._users:
            return

        with self.context as ctx:
            ctx.add_hook("show-secrets", functools.partial(self._show_secret,
                                                           name))

        obj = {
            "kind": "v2/database/postgres/user",
            "name": f"{self.name}-user-{name}",
            "owner": self.name,
            "depends_on": self._cluster_name,
            "cluster_id": self._cluster_id,
            "user": name,
            "params": {
                "name": name
            }
        }

        self.interfaces.do.add_object(obj)
        self._users[name] = f"{self.name}-user-{name}"

    def _resolve_uri(self, database: str, user: str) -> str:
        """TODO"""

        with self.context as ctx:
            password = ctx.get_secret_data(self._users[user], "password")

        metadata = self.interfaces.do.object_metadata(self._cluster_name)

        host = metadata["host"]
        port = metadata["port"]
        ssl = metadata["ssl"]

        if ssl:
            params = "sslmode=require&"

        return f"postgres://{user}:{password}@{host}:{port}/{database}?{params}"

    def uri(self, database: str, user: str) -> v1.utils.Future[str]:
        """TODO"""

        with self._lock:
            self._create_database(database)
            self._create_user(user)

        return v1.utils.Future(functools.partial(self._resolve_uri, database, user))


dolib.HANDLERS.update({
    "v2/database/postgres": _V2PostgresCluster,
    "v2/database/postgres/db": _V2PostgresDatabase,
    "v2/database/postgres/user": _V2PostgresUser
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1Cluster
        ]
    }
}
