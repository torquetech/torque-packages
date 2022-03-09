# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import io
import schema
import yaml

from torque import options


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


def _from_configuration(configuration: dict[str, str]) -> dict[str, str]:
    """TODO"""

    return [
        {"name": name, "value": value} for name, value in configuration.items()
    ]


def _from_object(name: str, configuration: dict[str, object]) -> dict[str, object]:
    """TODO"""

    return {
        "name": name,
        "configuration": _from_configuration(configuration)
    }


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

    def dump(self, stream: io.TextIOWrapper):
        """TODO"""

        config = {
            "providers": [],
            "dag": {}
        }

        providers = self.config["providers"]
        config["providers"] = [_from_object(*i) for i in providers.items()]

        dag = self.config["dag"]
        dag_config = config["dag"]

        dag_config["revision"] = dag["revision"]
        dag_config["clusters"] = [_from_object(*i) for i in dag["clusters"].items()]
        dag_config["components"] = [_from_object(*i) for i in dag["components"].items()]
        dag_config["links"] = [_from_object(*i) for i in dag["links"].items()]

        yaml.safe_dump(config,
                       stream=stream,
                       default_flow_style=False,
                       sort_keys=False)


def _to_raw_options(config: list[dict[str, str]]) -> options.RawOptions:
    return options.RawOptions({i["name"]: i["value"] for i in config})


def create(config: dict[str, object]) -> Configuration:
    """TODO"""

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
