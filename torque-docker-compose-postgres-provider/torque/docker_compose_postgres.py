# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import hashlib

import jinja2

from torque import docker_compose
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
            "dc": {
                "interface": docker_compose.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sanitized_name = self.name.replace(".", "-")

        self._databases = {}
        self._users = {}

        self._image = f"postgres:{self.configuration['version']}"
        self._password = self._create_access("postgres", "postgres")

        with self.context as ctx:
            ctx.add_hook("apply", self._create_init, add_before=docker_compose.V1Provider)

    def _create_init(self):
        """TODO"""

        local_sql_path = f"{self.context.path()}/{self.name}.sql"
        external_sql_path = f"{self.context.external_path()}/{self.name}.sql"

        sql = _INIT_SQL.render(databases=self._databases, users=self._users)
        sql_hash = hashlib.sha1(bytes(sql, encoding="utf-8"))

        with open(local_sql_path, "w", encoding="utf-8") as f:
            f.write(sql)

        self.interfaces.dc.add_object("configs", self._sanitized_name, {
            "file": external_sql_path
        })

        self.interfaces.dc.add_object("services", f"{self._sanitized_name}-init", {
            "image": f"postgres:{self.configuration['version']}",
            "labels": {
                "sql_hash": sql_hash.hexdigest()
            },
            "command": [
                "psql",
                "-h", self._sanitized_name,
                "-U", "postgres",
                "-f", "/init.sql",
                "postgres"
            ],
            "restart": "no",
            "environment": {
                "PGPASSWORD": self._password
            },
            "configs": [{
                "source": self._sanitized_name,
                "target": "/init.sql"
            }],
            "depends_on": {
                self._sanitized_name: {
                    "condition": "service_healthy"
                }
            }
        })

    def create(self):
        """TODO"""

        self.interfaces.dc.add_object("volumes", self._sanitized_name, {})

        self.interfaces.dc.add_object("services", self._sanitized_name, {
            "image": self._image,
            "restart": "unless-stopped",
            "environment": {
                "PGDATA": "/data",
                "POSTGRES_DB": "postgres",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": self._password
            },
            "volumes": [{
                "type": "volume",
                "source": self._sanitized_name,
                "target": "/data"
            }],
            "healthcheck": {
                "test": "pg_isready -U postgres",
                "interval": "10s",
                "timeout": "3s",
                "retries": 3
            }
        })

    def _show_secret(self, user: str):
        """TODO"""

        print(f"{self.name}: user: {user}, password: {self._users[user]}")

    def _create_access(self, database: str, user: str):
        """TODO"""

        with self.context as ctx:
            if database not in self._databases:
                self._databases[database] = set()

            if user not in self._users:
                self._users[user] = ctx.secret(self.name, user)

                ctx.add_hook("show-secrets", functools.partial(self._show_secret,
                                                               user))

            self._databases[database].add(user)

            return self._users[user]

    def uri(self, database: str, user: str) -> v1.utils.Future[str]:
        """TODO"""

        password = self._create_access(database, user)

        return \
            f"postgres://{user}:{password}@" \
            f"{self._sanitized_name}:5432/{database}?sslmode=disable"


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
