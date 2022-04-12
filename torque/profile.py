# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import re
import schema
import yaml

from torque import model
from torque import repository

from torque.v1 import utils as utils_v1


_PROTO = r"^([^:]+)://"
_CONFIGURATION_SCHEMA = schema.Schema({
    "provider": {
        schema.Optional(str): object,
    },
    "dag": {
        "revision": int,
        "components": {
            schema.Optional(str): object
        },
        "links": {
            schema.Optional(str): object
        }
    }
})


class Profile:
    """TODO"""

    def __init__(self, config: dict[str, object]):
        self.config = config

    def revision(self) -> int:
        """TODO"""

        return self.config["dag"]["revision"]

    def provider(self) -> (str, object):
        """TODO"""

        return list(self.config["provider"].items())[0]

    def component(self, name: str) -> object:
        """TODO"""

        dag_config = self.config["dag"]
        components = dag_config["components"]

        if name not in components:
            return {}

        return components[name]

    def link(self, name: str) -> object:
        """TODO"""

        dag_config = self.config["dag"]
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


def load(uris: [str], repo: repository.Repository) -> Profile:
    """TODO"""

    configuration = {}

    for uri in uris:
        configuration = utils_v1.merge_dicts(configuration, _load_configuration(uri, repo), False)

    return Profile(_CONFIGURATION_SCHEMA.validate(configuration))


def defaults(provider: str,
             dag: model.DAG,
             repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    return {
        "provider": {
            provider: repo.provider(provider).validate_configuration({})
        },
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: repo.component(component.type).validate_configuration({}) or {}
                for component in dag.components.values()
            },
            "links": {
                link.name: repo.link(link.type).validate_configuration({}) or {}
                for link in dag.links.values()
            }
        }
    }
