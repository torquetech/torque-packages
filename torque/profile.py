# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import re
import yaml

from torque import model
from torque import repository
from torque import v1


_PROTO = r"^([^:]+)://"
_CONFIGURATION_SCHEMA = v1.schema.Schema({
    "providers": {
        v1.schema.Optional(str): {
            "configuration": dict
        }
    },
    "binds": {
        v1.schema.Optional(str): {
            "configuration": dict
        }
    },
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): {
                "configuration": dict,
                v1.schema.Optional("binds"): {
                    v1.schema.Optional(str): {
                        "configuration": dict
                    }
                }
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "configuration": dict
            }
        }
    }
})


class Profile:
    """TODO"""

    def __init__(self, name: str, config: dict[str, object]):
        self.name = name
        self._config = config

    def _component(self, name: str) -> dict:
        """TODO"""

        dag_config = self._config["dag"]
        components = dag_config["components"]

        if name not in components:
            return {}

        return components[name]

    def revision(self) -> int:
        """TODO"""

        return self._config["dag"]["revision"]

    def providers(self) -> [str]:
        """TODO"""

        return self._config["providers"].keys()

    def binds(self) -> [str]:
        """TODO"""

        return self._config["binds"].keys()

    def provider(self, name: str) -> dict:
        """TODO"""

        providers = self._config["providers"]

        if name not in providers:
            return {}

        return providers[name]["configuration"]

    def bind(self, name: str) -> dict:
        """TODO"""

        binds = self._config["binds"]

        if name not in binds:
            return {}

        return binds[name]["configuration"]

    def component_binds(self, name: str) -> dict:
        """TODO"""

        component = self._component(name)

        if not component:
            return {}

        if "binds" not in component:
            return {}

        return component["binds"]

    def component(self, name: str) -> dict:
        """TODO"""

        component = self._component(name)

        if not component:
            return {}

        return component["configuration"]

    def link(self, name: str) -> dict:
        """TODO"""

        dag_config = self._config["dag"]
        links = dag_config["links"]

        if name not in links:
            return {}

        return links[name]["configuration"]


def _load_configuration(uri: str, repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    match = re.match(_PROTO, uri)

    if match:
        proto = match[0]

    else:
        proto = "file://"

    proto = proto.rstrip("://")
    proto = repo.protocol(proto)
    proto = proto()

    with proto.fetch(uri) as file:
        return yaml.safe_load(file)


def load(name: str, uris: [str], repo: repository.Repository) -> Profile:
    """TODO"""

    configuration = {}

    for uri in uris:
        configuration = v1.utils.merge_dicts(configuration,
                                             _load_configuration(uri, repo),
                                             True)

    try:
        return Profile(name, _CONFIGURATION_SCHEMA.validate(configuration))

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"profile: {name}: {exc}") from exc


def defaults(providers: [str],
             dag: model.DAG,
             repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    binds = []

    for provider_name in providers:
        for bind_name, mapped_provider_name in repo.bind_maps().items():
            if provider_name == mapped_provider_name:
                binds.append(bind_name)

    return {
        "providers": {
            name: {
                "configuration": repo.provider(name).on_configuration({})
            } for name in providers
        },
        "binds": {
            name: {
                "configuration": repo.bind(name).on_configuration({})
            } for name in binds
        },
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: {
                    "configuration": repo.component(component.type).on_configuration({}) or {}
                } for component in dag.components.values()
            },
            "links": {
                link.name: {
                    "configuration": repo.link(link.type).on_configuration({}) or {}
                } for link in dag.links.values()
            }
        }
    }
