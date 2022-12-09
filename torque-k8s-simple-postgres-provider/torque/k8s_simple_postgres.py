# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# This file contains k8s yaml files generated from ingress-nginx helm
# repository. For more details, visit https://kubernetes.github.io/ingress-nginx/

"""TODO"""

import hashlib

import jinja2

from torque import k8s
from torque import k8s_volumes
from torque import postgres
from torque import v1


_INIT_SQL = jinja2.Template("""
{%- for user, password in users.items() %}
{%- if user != 'postgres' -%}
create user {{user}} with createdb createrole password '{{password}}';
{% endif -%}
{%- endfor %}
{% for database, users in databases.items() %}
{%- if database != 'postgres' -%}
create database {{database}};
{% endif -%}
{%- endfor %}
{% for database, users in databases.items() -%}
{% for user in users -%}
{%- if user != 'postgres' -%}
grant all privileges on database {{database}} to {{user}};
{% endif -%}
{%- endfor -%}
{%- endfor -%}
""")


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1Implementation(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = postgres.V1ImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "version": "14"
        },
        "schema": {
            "version": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": k8s.V1Provider,
                "required": True
            },
            "vol": {
                "interface": k8s_volumes.V1Interface,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._namespace = self.interfaces.k8s.namespace()

        self._databases = {}
        self._users = {}

        with self.interfaces.k8s as p:
            p.add_hook("apply-objects", self._apply)

    def _create_access(self, database: str, user: str):
        """TODO"""

        with self.context as ctx:
            if database not in self._databases:
                self._databases[database] = set()

            if user not in self._users:
                self._users[user] = ctx.secret(self.name, user)

            self._databases[database].add(user)

            return self._users[user]

    def _apply(self):
        """TODO"""

        image = f"postgres:{self.configuration['version']}"
        password = self._create_access("postgres", "postgres")

        sql = _INIT_SQL.render(databases=self._databases, users=self._users)
        sql_hash = hashlib.sha1(bytes(sql, encoding="utf-8"))

        volume_mounts = []
        volumes = []

        if self.interfaces.vol:
            volume_mounts = [{
                "name": self.interfaces.vol.ref_name(),
                "mountPath": "/data"
            }]

            volumes = [
                self.interfaces.vol.spec()
            ]

        self.interfaces.k8s.add_object({
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.name,
                "namespace": self._namespace,
                "labels": {
                    "app.kubernetes.io/name": self.name
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": self.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app.kubernetes.io/name": self.name
                        }
                    },
                    "spec": {
                        "restartPolicy": "Always",
                        "containers": [{
                            "name": "main",
                            "image": image,
                            "env": [{
                                "name": "PGDATA",
                                "value": "/data/pg"
                            }, {
                                "name": "POSTGRES_DB",
                                "value": "postgres"
                            }, {
                                "name": "POSTGRES_USER",
                                "value": "postgres"
                            }, {
                                "name": "POSTGRES_PASSWORD",
                                "value": password
                            }],
                            "volumeMounts": volume_mounts
                        }],
                        "volumes": volumes
                    }
                }
            }
        })

        self.interfaces.k8s.add_object({
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self.name,
                "namespace": self._namespace
            },
            "spec": {
                "selector": {
                    "app.kubernetes.io/name": self.name
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": 5432,
                    "targetPort": 5432
                }]
            }
        })

        self.interfaces.k8s.add_object({
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": self.name,
                "namespace": self._namespace
            },
            "data": {
                "init.sql": sql
            }
        })

        self.interfaces.k8s.add_object({
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": f"{self.name}-init-{sql_hash.hexdigest()}",
                "namespace": self._namespace
            },
            "spec": {
                "restartPolicy": "OnFailure",
                "containers": [{
                    "name": "main",
                    "image": image,
                    "command": [
                        "psql",
                        "-h", self.name,
                        "-U", "postgres",
                        "-f", "/init.sql",
                        "postgres"
                    ],
                    "env": [{
                        "name": "PGPASSWORD",
                        "value": password
                    }],
                    "volumeMounts": [{
                        "name": "config",
                        "mountPath": "/init.sql",
                        "subPath": "init.sql"
                    }]
                }],
                "volumes": [{
                    "name": "config",
                    "configMap": {
                        "name": self.name
                    }
                }]
            }
        })

    def auth(self, database: str, user: str) -> v1.utils.Future[postgres.Authorization]:
        """TODO"""

        return v1.utils.Future(postgres.Authorization(database,
                                                      user,
                                                      self._create_access(database, user)))

    def service(self) -> postgres.Service:
        """TODO"""

        host = f"{self.name}.{self._namespace}"

        return postgres.Service(host, 5432, {
            "sslmode": "disable"
        })


repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1Implementation
        ]
    }
}
