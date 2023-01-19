# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import hashlib

import jinja2

from torque import docker_compose
from torque import postgres
from torque import v1


_INIT_SQL = jinja2.Template("""
{%- for user, password in users.items() | sort %}
{%- if user != 'postgres' -%}
create user {{user}} with createdb createrole password '{{password}}';
{% endif -%}
{%- endfor %}
{% for database, users in databases.items() | sort %}
{%- if database != 'postgres' -%}
create database {{database}};
{% endif -%}
{%- endfor %}
{% for database, users in databases.items() | sort -%}
{% for user in users | sort -%}
{%- if user != 'postgres' -%}
grant all privileges on database {{database}} to {{user}};
{% endif -%}
{%- endfor -%}
{%- endfor -%}
""")


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""


class V1Implementation(v1.bond.Bond):
    """DOCSTRING"""

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
        """DOCSTRING"""

        return {
            "dc": {
                "interface": docker_compose.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._databases = {}
        self._users = {}

        with self.interfaces.dc as p:
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

        image = f"postgres:{self.configuration['version']}"
        password = self._create_access("postgres", "postgres")

        local_sql_path = f"{self.context.path()}/{self.name}.sql"
        external_sql_path = f"{self.context.external_path()}/{self.name}.sql"

        sql = _INIT_SQL.render(databases=self._databases, users=self._users)
        sql_hash = hashlib.sha1(bytes(sql, encoding="utf-8"))

        with open(local_sql_path, "w", encoding="utf-8") as f:
            f.write(sql)

        self.interfaces.dc.add_object("volumes", self.name, {})

        self.interfaces.dc.add_object("configs", self.name, {
            "file": external_sql_path
        })

        self.interfaces.dc.add_object("services", f"{self.name}-init", {
            "image": image,
            "labels": {
                "sql_hash": sql_hash.hexdigest()
            },
            "command": [
                "psql",
                "-h", self.name,
                "-U", "postgres",
                "-f", "/init.sql",
                "postgres"
            ],
            "restart": "no",
            "environment": {
                "PGPASSWORD": password
            },
            "configs": [{
                "source": self.name,
                "target": "/init.sql"
            }],
            "depends_on": {
                self.name: {
                    "condition": "service_healthy"
                }
            }
        })

        self.interfaces.dc.add_object("services", self.name, {
            "image": image,
            "restart": "unless-stopped",
            "environment": {
                "PGDATA": "/data",
                "POSTGRES_DB": "postgres",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": password
            },
            "volumes": [{
                "type": "volume",
                "source": self.name,
                "target": "/data"
            }],
            "healthcheck": {
                "test": "pg_isready -U postgres",
                "interval": "10s",
                "timeout": "3s",
                "retries": 3
            }
        })

    def auth(self, database: str, user: str) -> v1.utils.Future[postgres.Authorization]:
        """DOCSTRING"""

        return v1.utils.Future(postgres.Authorization(database,
                                                      user,
                                                      self._create_access(database, user)))

    def service(self) -> v1.utils.Future[postgres.Service]:
        """DOCSTRING"""

        return v1.utils.Future(postgres.Service(self.name, 5432, {
            "sslmode": "disable"
        }))


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
