# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import hashlib

import jinja2

from torque import docker_compose
from torque import docker_compose_load_balancer
from torque import hlb
from torque import v1


_INGRESS_LB = jinja2.Template("""
resolver 127.0.0.11;
{% for host in hosts %}
server {
  listen 80;
  server_name {{host}}.{{domain}};
{%- for ingress in ingress_list -%}
{%- if host == ingress.host %}

  location {{ingress.path}} {
    set $base {{ingress.service}}:{{ingress.port}};
    proxy_pass http://$base$request_uri;
    proxy_pass_request_headers on;
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header Host $host;
{%- if "websocket" in ingress.options %}
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_cache_bypass $http_upgrade;
{%- endif %}
  }
{%- endif -%}
{% endfor %}
}
{% endfor -%}
""")


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""


class V1Implementation(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = hlb.V1ImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "domain": "example.com"
        },
        "schema": {
            "domain": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "dc": {
                "interface": docker_compose.V1Provider,
                "required": True
            },
            "lb": {
                "interface": docker_compose_load_balancer.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ingress_list = []

        with self.interfaces.dc as p:
            p.add_hook("apply-objects", self._apply)

    def _apply(self):
        """DOCSTRING"""

        ingress_list = [
            v1.utils.resolve_futures(i) for i in self._ingress_list
        ]

        domain = self.configuration["domain"]
        hosts = sorted(list({i.host for i in ingress_list}))

        self.interfaces.lb.add_entry(docker_compose_load_balancer.Entry(self.name,
                                                                        domain,
                                                                        hosts))

        conf = _INGRESS_LB.render(domain=domain, hosts=hosts, ingress_list=ingress_list)
        conf_hash = hashlib.sha1(bytes(conf, encoding="utf-8"))

        local_conf = f"{self.context.path()}/{self.name}.conf"
        external_conf = f"{self.context.external_path()}/{self.name}.conf"

        with open(local_conf, "w", encoding="utf-8") as f:
            f.write(conf)

        self.interfaces.dc.add_object("configs", self.name, {
            "file": external_conf
        })

        self.interfaces.dc.add_object("services", self.name, {
            "image": "nginx:latest",
            "labels": {
                "conf_hash": conf_hash.hexdigest()
            },
            "restart": "unless-stopped",
            "configs": [{
                "source": self.name,
                "target": "/etc/nginx/conf.d/ingress.conf"
            }]
        })

    def add(self, ingress: hlb.Ingress):
        """DOCSTRING"""

        self._ingress_list.append(ingress)


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
