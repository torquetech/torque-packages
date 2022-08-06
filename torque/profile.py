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
    "version": str,
    "providers": {
        v1.schema.Optional(str): {
            "labels": [str],
            "configuration": dict,
            "binds": {
                v1.schema.Optional(str): {
                    "configuration": dict
                }
            },
            "interfaces": {
                v1.schema.Optional(str): {
                    "bind": str
                }
            }
        }
    },
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): {
                "configuration": dict,
                "binds": {
                    v1.schema.Optional(str): {
                        "configuration": dict
                    }
                },
                "interfaces": {
                    v1.schema.Optional(str): {
                        "bind": str
                    }
                }
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "configuration": dict
            }
        }
    },
    "binds": {
        v1.schema.Optional(str): {
            "configuration": dict
        }
    },
    "interfaces": {
        v1.schema.Optional(str): {
            "bind": str
        }
    }
})


class Profile:
    """TODO"""

    def __init__(self, name: str, config: dict[str, object]):
        self.name = name
        self._config = config

    def revision(self) -> int:
        """TODO"""

        return self._config["dag"]["revision"]

    def providers(self) -> [str]:
        """TODO"""

        return self._config["providers"].keys()

    def binds(self) -> [str]:
        """TODO"""

        return self._config["binds"].keys()

    def interfaces(self) -> [str]:
        """TODO"""

        return self._config["interfaces"].keys()

    def provider(self, name: str) -> dict:
        """TODO"""

        return self._config["providers"][name]

    def bind(self, name: str) -> dict:
        """TODO"""

        return self._config["binds"][name]

    def interface(self, name: str) -> dict:
        """TODO"""

        return self._config["interfaces"][name]

    def component(self, name: str) -> dict:
        """TODO"""

        dag_config = self._config["dag"]

        return dag_config["components"][name]

    def link(self, name: str) -> dict:
        """TODO"""

        dag_config = self._config["dag"]

        return dag_config["links"][name]


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
        configuration = _CONFIGURATION_SCHEMA.validate(configuration)

    except v1.schema.SchemaError as exc:
        exc_str = str(exc)
        exc_str = " " + exc_str.replace("\n", "\n ")

        raise RuntimeError(f"profile: {name}:\n{exc_str}") from exc

    if configuration["version"] != "torquetech.dev/v1":
        raise RuntimeError(f"{configuration['version']}: invalid configuration version")

    return Profile(name, configuration)


def defaults(providers: [str],
             dag: model.DAG,
             repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    provider_binds = []

    for provider_name in providers:
        for bind_name, mapped_provider_name in repo.bind_maps().items():
            if provider_name == mapped_provider_name:
                provider_binds.append(bind_name)

    interfaces = {}
    binds = {}

    for interface_name, interface_class in repo.interfaces().items():
        bind = None

        for bind_name in provider_binds:
            if issubclass(repo.bind(bind_name), interface_class):
                if not bind:
                    bind = bind_name

                binds[bind_name] = {
                    "configuration": repo.bind(bind_name).on_configuration({})
                }

        if bind:
            interfaces[interface_name] = {
                "bind": bind,
            }

    return {
        "version": "torquetech.dev/v1",
        "providers": {
            name: {
                "labels": [],
                "configuration": repo.provider(name).on_configuration({}),
                "binds": {},
                "interfaces": {}
            } for name in providers
        },
        "binds": binds,
        "interfaces": interfaces,
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: {
                    "configuration": repo.component(component.type).on_configuration({}) or {},
                    "binds": {},
                    "interfaces": {}
                } for component in dag.components.values()
            },
            "links": {
                link.name: {
                    "configuration": repo.link(link.type).on_configuration({}) or {}
                } for link in dag.links.values()
            }
        }
    }
