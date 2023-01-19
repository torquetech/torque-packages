# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import hashlib

import jinja2

from torque import k8s
from torque import k8s_volumes
from torque import mysql
from torque import v1


_INIT_SQL = jinja2.Template("""
{%- for user, password in users.items() | sort %}
{%- if user != 'mysql' -%}
create user {{user}} identified by '{{password}}';
{% endif -%}
{%- endfor %}
{% for database, users in databases.items() | sort %}
{%- if database != 'mysql' -%}
create database {{database}};
{% endif -%}
{%- endfor %}
{% for database, users in databases.items() | sort -%}
{% for user in users | sort -%}
{%- if user != 'mysql' -%}
grant all on {{database}}.* to {{user}};
{% endif -%}
{%- endfor -%}
{%- endfor -%}
""")


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""


class V1Implementation(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = mysql.V1ImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "version": "8"
        },
        "schema": {
            "version": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

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
        """DOCSTRING"""

        with self.context as ctx:
            if database not in self._databases:
                self._databases[database] = set()

            if user not in self._users:
                self._users[user] = ctx.secret(self.name, user)

            self._databases[database].add(user)

            return self._users[user]

    def _apply(self):
        """DOCSTRING"""

        image = f"mysql:{self.configuration['version']}"
        password = self._create_access("mysql", "mysql")

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
                                "name": "MYSQL_DATABASE",
                                "value": "mysql"
                            }, {
                                "name": "MYSQL_ROOT_PASSWORD",
                                "value": password
                            }, {
                                "name": "MYSQL_USER",
                                "value": "mysql"
                            }, {
                                "name": "MYSQL_PASSWORD",
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
                    "port": 3306,
                    "targetPort": 3306
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
                        "bash", "-c",
                        f"mysql --host={self.name} --user=root -f < /init.sql"
                    ],
                    "env": [{
                        "name": "MYSQL_PWD",
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

    def auth(self, database: str, user: str) -> v1.utils.Future[mysql.Authorization]:
        """DOCSTRING"""

        return v1.utils.Future(mysql.Authorization(database,
                                                   user,
                                                   self._create_access(database, user)))

    def service(self) -> v1.utils.Future[mysql.Service]:
        """DOCSTRING"""

        host = f"{self.name}.{self._namespace}"

        return v1.utils.Future(mysql.Service(host, 3306, {}))


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
