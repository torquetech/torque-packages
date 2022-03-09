# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import schema
import yaml

from collections import namedtuple
from importlib import metadata

from torque import model


Profile = namedtuple("Profile", ["name", "uri", "secret"])
Profiles = dict[str, Profile]


_CONFIG_SCHEMA = schema.Schema({
    "profiles": [{
        "name": str,
        "uri": str,
        "secret": str
    }],
    "dag": {
        "revision": int,
        "clusters": [{
            "name": str
        }],
        "components": [{
            "name": str,
            "cluster": str,
            "type": str,
            "params": [{
                "name": str,
                "value": str
            }]
        }],
        "links": [{
            "name": str,
            "source": str,
            "destination": str,
            "type": str,
            "params": [{
                "name": str,
                "value": str
            }]
        }]
    }
})


def _to_profile(config: dict[str, object]) -> Profile:
    """TODO"""

    return Profile(config["name"],
                   config["uri"],
                   config["secret"])


def _from_profiles(profiles: Profiles) -> list[dict[str, object]]:
    """TODO"""

    return [
        {"name": i.name, "uri": i.uri, "secret": i.secret} for i in profiles.values()
    ]


def _from_cluster(cluster: model.Cluster) -> dict[str: str]:
    """TODO"""

    return {
        "name": cluster.name
    }


def _from_params(params: dict[str, str]) -> list[dict[str, str]]:
    """TODO"""

    return [
        {"name": name, "value": value} for name, value in params.items()
    ]


def _from_component(component: model.Component) -> dict[str: object]:
    """TODO"""

    return {
        "name": component.name,
        "cluster": component.cluster,
        "type": component.component_type,
        "params": _from_params(component.params)
    }


def _from_link(link: model.Link) -> dict[str: object]:
    """TODO"""

    return {
        "name": link.name,
        "source": link.source,
        "destination": link.destination,
        "type": link.link_type,
        "params": _from_params(link.params)
    }


def _generate_dag(config: dict[str, object], modules: model.Modules) -> model.DAG:
    """TODO"""

    config_dag = config["dag"]
    dag = model.DAG(config_dag["revision"], modules)

    for cluster in config_dag["clusters"]:
        dag.create_cluster(cluster["name"])

    for component in config_dag["components"]:
        params = {i["name"]: i["value"] for i in component["params"]}

        dag.create_component(component["name"],
                             component["cluster"],
                             component["type"],
                             params)

    for link in config_dag["links"]:
        params = {i["name"]: i["value"] for i in link["params"]}

        dag.create_link(link["name"],
                        link["source"],
                        link["destination"],
                        link["type"],
                        params)

    dag.verify()

    return dag


def load(path: str, extra_modules: model.Modules = None) -> (model.DAG, Profiles):
    """TODO"""

    config = {
        "profiles": [],
        "dag": {
            "revision": 0,
            "clusters": [],
            "components": [],
            "links": []
        }
    }

    try:
        with open(path, encoding="utf8") as file:
            config = config | yaml.safe_load(file)

    except FileNotFoundError:
        pass

    _CONFIG_SCHEMA.validate(config)

    profiles = {i["name"]: _to_profile(i) for i in config["profiles"]}
    modules = {}

    entry_points = metadata.entry_points()

    if "torque.components.v1" in entry_points:
        modules["components.v1"] = {i.name: i.load() for i in entry_points["torque.components.v1"]}

    else:
        modules["components.v1"] = {}

    if "torque.links.v1" in entry_points:
        modules["links.v1"] = {i.name: i.load() for i in entry_points["torque.links.v1"]}

    else:
        modules["links.v1"] = {}

    if extra_modules:
        modules = modules | extra_modules

    dag = _generate_dag(config, modules)

    return dag, profiles


def store(path: str, dag: model.DAG, profiles: Profiles):
    """TODO"""

    config = {
        "profiles": [],
        "dag": {
            "revision": 0,
            "clusters": [],
            "components": [],
            "links": []
        }
    }

    config_dag = config["dag"]

    config_dag["revision"] = dag.revision + 1
    config_dag["clusters"] = [_from_cluster(i) for i in dag.clusters.values()]
    config_dag["components"] = [_from_component(i) for i in dag.components.values()]
    config_dag["links"] = [_from_link(i) for i in dag.links.values()]

    config["profiles"] = _from_profiles(profiles)

    with open(f"{path}.tmp", "w", encoding="utf8") as file:
        yaml.safe_dump(config,
                       stream=file,
                       default_flow_style=False,
                       sort_keys=False)

    os.replace(f"{path}.tmp", path)
