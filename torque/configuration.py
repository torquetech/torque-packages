# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import re
import schema
import yaml

from torque import exceptions
from torque import internal
from torque import model
from torque import options


_PROTO = r"^([^:]+)://"
_CONFIG_SCHEMA = schema.Schema({
    "providers": [{
        "name": str,
        "configuration": [{
            "name": str,
            "value": str
        }]
    }],
    "dag": {
        "revision": int,
        "clusters": [{
            "name": str,
            "configuration": [{
                "name": str,
                "value": str
            }]
        }],
        "components": [{
            "name": str,
            "configuration": [{
                "name": str,
                "value": str
            }]
        }],
        "links": [{
            "name": str,
            "configuration": [{
                "name": str,
                "value": str
            }]
        }]
    }
})


def _proto_file(uri: str, secret: str) -> dict[str, object]:
    # pylint: disable=W0613

    """TODO"""

    with open(uri, encoding="utf8") as file:
        return yaml.safe_load(file)


internal.TYPES["proto.v1"]["file"] = _proto_file
# internal.TYPES["proto.v1"]["https"] = _proto_https
# internal.TYPES["proto.v1"]["http"] = _proto_http


class Configuration:
    """TODO"""

    def __init__(self, config: dict[str, object]):
        self.config = config

    def get_provider(self, name: str) -> options.RawOptions:
        """TODO"""

        providers = self.config["providers"]

        if name not in providers:
            return options.RawOptions()

        return providers[name]

    def get_cluster(self, name: str) -> options.RawOptions:
        """TODO"""

        dag_config = self.config["dag"]
        clusters = dag_config["clusters"]

        if name not in clusters:
            return options.RawOptions()

        return clusters[name]

    def get_component(self, name: str) -> options.RawOptions:
        """TODO"""

        dag_config = self.config["dag"]
        components = dag_config["components"]

        if name not in components:
            return options.RawOptions()

        return components[name]

    def get_link(self, name: str) -> options.RawOptions:
        """TODO"""

        dag_config = self.config["dag"]
        links = dag_config["links"]

        if name not in links:
            return options.RawOptions()

        return links[name]


def _to_raw_options(config: list[dict[str, str]]) -> options.RawOptions:
    return options.RawOptions({i["name"]: i["value"] for i in config})


def load(uri: str, secret: str, types: model.Types) -> Configuration:
    """TODO"""

    proto = "file"
    match = re.match(_PROTO, uri)

    if match:
        proto = match[1]

    protos = types["proto.v1"]

    if proto not in protos:
        raise exceptions.ProtocolNotSupported(proto)

    proto_handler = protos[proto]

    config = proto_handler(uri, secret)
    _CONFIG_SCHEMA.validate(config)

    config["providers"] = {
        i["name"]: _to_raw_options(i["configuration"]) for i in config["providers"]
    }

    dag_config = config["dag"]

    dag_config["clusters"] = {
        i["name"]: _to_raw_options(i["configuration"]) for i in dag_config["clusters"]
    }

    dag_config["components"] = {
        i["name"]: _to_raw_options(i["configuration"]) for i in dag_config["components"]
    }

    dag_config["links"] = {
        i["name"]: _to_raw_options(i["configuration"]) for i in dag_config["links"]
    }

    return Configuration(config)
