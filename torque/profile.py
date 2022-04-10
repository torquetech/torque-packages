# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import re
import schema
import yaml

from torque import model
from torque import extensions
from torque import options
from torque import utils


_PROTO = r"^([^:]+)://"
_CONFIG_SCHEMA = schema.Schema({
    "provider": {
        "name": str,
        "configuration": [{
            "name": str,
            "value": object
        }]
    },
    "dag": {
        "revision": int,
        "components": [{
            "name": str,
            "configuration": [{
                "name": str,
                "value": object
            }]
        }],
        "links": [{
            "name": str,
            "configuration": [{
                "name": str,
                "value": object
            }]
        }]
    }
})


class Profile:
    """TODO"""

    def __init__(self, config: dict[str, object]):
        self.config = config

    def revision(self) -> int:
        """TODO"""

        return self.config["dag"]["revision"]

    def provider(self) -> options.RawOptions:
        """TODO"""

        return list(self.config["provider"].items())[0]

    def component(self, name: str) -> (str, options.RawOptions):
        """TODO"""

        dag_config = self.config["dag"]
        components = dag_config["components"]

        if name not in components:
            return (name, options.RawOptions())

        return (name, components[name])

    def link(self, name: str) -> (str, options.RawOptions):
        """TODO"""

        dag_config = self.config["dag"]
        links = dag_config["links"]

        if name not in links:
            return (name, options.RawOptions())

        return (name, links[name])


def _load_config(uri: str, exts: extensions.Extensions) -> dict[str, object]:
    """TODO"""

    match = re.match(_PROTO, uri)

    if match:
        proto = match[0]

    else:
        proto = "file://"

    proto = proto.rstrip("://")
    proto = exts.protocol(proto)
    proto = proto()

    with proto.fetch(uri) as file:
        return yaml.safe_load(file)


def _to_raw(config: list[dict[str, str]]) -> options.RawOptions:
    """TODO"""

    return options.RawOptions({i["name"]: i["value"] for i in config})


def load(uris: [str], exts: extensions.Extensions) -> Profile:
    """TODO"""

    config = {}

    for uri in uris:
        config = utils.merge_dicts(config, _load_config(uri, exts), False)

    config = _CONFIG_SCHEMA.validate(config)

    provider = config["provider"]
    dag = config["dag"]

    _config = {
        "provider": {
            provider["name"]: _to_raw(provider["configuration"])
        },
        "dag": {
            "revision": dag["revision"],
            "components": {
                i["name"]: _to_raw(i["configuration"]) for i in dag["components"]
            },
            "links": {
                i["name"]: _to_raw(i["configuration"]) for i in dag["links"]
            }
        }
    }

    return Profile(_config)


def defaults(provider: str,
             dag: model.DAG,
             exts: extensions.Extensions) -> dict[str, object]:
    """TODO"""

    provider_conf = exts.provider(provider).configuration()

    defaults = {
        "provider": {
            "name": provider,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in provider_conf
            ]
        },
        "dag": {
            "revision": dag.revision,
            "components": [],
            "links": []
        }
    }

    components = defaults["dag"]["components"]
    links = defaults["dag"]["links"]

    for component in dag.components.values():
        component_conf = exts.component(component.type).configuration()
        components.append({
            "name": component.name,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in component_conf
            ]
        })

    for link in dag.links.values():
        link_conf = exts.link(link.type).configuration()
        links.append({
            "name": link.name,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in link_conf
            ]
        })

    return defaults
