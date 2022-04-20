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
        v1.schema.Optional(str): object,
    },
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): object
        },
        "links": {
            v1.schema.Optional(str): object
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

    def provider(self, name: str) -> object:
        """TODO"""

        providers = self._config["providers"]

        if name not in providers:
            return {}

        return providers[name]

    def component(self, name: str) -> object:
        """TODO"""

        dag_config = self._config["dag"]
        components = dag_config["components"]

        if name not in components:
            return {}

        return components[name]

    def link(self, name: str) -> object:
        """TODO"""

        dag_config = self._config["dag"]
        links = dag_config["links"]

        if name not in links:
            return {}

        return links[name]


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
        configuration = v1.utils.merge_dicts(configuration, _load_configuration(uri, repo), False)

    try:
        return Profile(name, _CONFIGURATION_SCHEMA.validate(configuration))

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"profile: {name}: {exc}") from exc


def defaults(providers: [str],
             dag: model.DAG,
             repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    return {
        "providers": {
            provider: repo.provider(provider).configuration({})
            for provider in providers
        },
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: repo.component(component.type).configuration({}) or {}
                for component in dag.components.values()
            },
            "links": {
                link.name: repo.link(link.type).configuration({}) or {}
                for link in dag.links.values()
            }
        }
    }
