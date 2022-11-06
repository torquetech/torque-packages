# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import hashlib

import jinja2

from torque import docker_compose
from torque import hlb
from torque import v1


_INGRESS_LB = jinja2.Template("""
{% for host in hosts %}
server {
  listen 80;
  server_name {{host}}.{{domain}};
{%- for ingress in ingress_list -%}
{%- if host == ingress.host %}

  location {{ingress.path}} {
    proxy_pass http://{{ingress.service}}:{{ingress.port}};
    proxy_set_header Host $host;
    proxy_pass_request_headers on;
  }
{%- endif -%}
{% endfor %}
}
{% endfor -%}
""")


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1Implementation(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = hlb.V1ImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "domain": "my-domain.com"
        },
        "schema": {
            "domain": str
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

    def create(self, ingress_list: [hlb.Ingress]):
        """TODO"""

        local_conf_path = f"{self.context.path()}/{self.name}.conf"
        external_conf_path = f"{self.context.external_path()}/{self.name}.conf"

        domain = self.configuration["domain"]
        hosts = sorted(list({i.host for i in ingress_list}))

        conf = _INGRESS_LB.render(domain=domain, hosts=hosts, ingress_list=ingress_list)
        conf_hash = hashlib.sha1(bytes(conf, encoding="utf-8"))

        with open(local_conf_path, "w", encoding="utf-8") as f:
            f.write(conf)

        self.interfaces.dc.add_object("configs", self._sanitized_name, {
            "file": external_conf_path
        })

        self.interfaces.dc.add_object("services", self._sanitized_name, {
            "image": "nginx:latest",
            "labels": {
                "conf_hash": conf_hash.hexdigest()
            },
            "restart": "unless-stopped",
            "configs": [{
                "source": self._sanitized_name,
                "target": "/etc/nginx/conf.d/ingress.conf"
            }]
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
