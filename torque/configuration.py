# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import yaml

from collections import namedtuple
from importlib import metadata
from schema import Schema

from torque.model import DAG


Profile = namedtuple("Profile", ["name", "uri", "secret"])
Cluster = namedtuple("Cluster", ["name"])
Component = namedtuple("Component", ["name", "cluster", "type", "params"])
Link = namedtuple("Link", ["name", "source", "destination", "type", "params"])
Param = namedtuple("Param", ["name", "value"])

Config = dict[str, object]


config_schema = Schema({
    "revision": int,
    "profiles": [{
        "name": str,
        "uri": str,
        "secret": str
    }],
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
})


def _to_profile(config: Config) -> Profile:
    """TODO"""

    return Profile(config["name"],
                   config["uri"],
                   config["secret"])


def _to_cluster(config: Config) -> Cluster:
    """TODO"""

    return Cluster(config["name"])


def _to_param(config: Config) -> Param:
    """TODO"""

    return Param(config["name"],
                 config["value"])


def _to_params(config: Config) -> list[Param]:
    """TODO"""

    return {i["name"]: _to_param(i) for i in config}


def _to_component(config: Config) -> Component:
    """TODO"""

    return Component(config["name"],
                     config["cluster"],
                     config["type"],
                     _to_params(config["params"]))


def _to_link(config: Config) -> Link:
    """TODO"""

    return Link(config["name"],
                config["source"],
                config["destination"],
                config["type"],
                _to_params(config["params"]))


def _from_profile(profile: Profile) -> Config:
    """TODO"""

    return {
        "name": profile.name,
        "uri": profile.uri,
        "secret": profile.secret
    }


def _from_cluster(cluster: Cluster) -> Config:
    """TODO"""

    return {
        "name": cluster.name
    }


def _from_param(param: Param) -> Config:
    """TODO"""

    return {
        "name": param.name,
        "value": param.value
    }


def _from_params(params: dict[str, Param]) -> Config:
    """TODO"""

    return [
        _from_param(i) for i in params.values()
    ]


def _from_component(component: Component) -> Config:
    """TODO"""

    return {
        "name": component.name,
        "cluster": component.cluster,
        "type": component.type,
        "params": _from_params(component.params)
    }


def _from_link(link: Link) -> Config:
    """TODO"""

    return {
        "name": link.name,
        "source": link.source,
        "destination": link.destination,
        "type": link.type,
        "params": _from_params(link.params)
    }


def generate_dag(config: Config) -> DAG:
    """TODO"""

    dag = DAG()

    for cluster in config["clusters"].values():
        dag.create_cluster(cluster.name)

    for component in config["components"].values():
        dag.create_component(component.name,
                             component.cluster,
                             component.type)

    for link in config["links"].values():
        dag.create_link(link.name,
                        link.source,
                        link.destination,
                        link.type)

    if dag.has_cycles():
        raise RuntimeError("cycle detected")

    return dag


def load(path: str) -> Config:
    """TODO"""

    stored_config = {
        "revision": 0,
        "profiles": [],
        "clusters": [],
        "components": [],
        "links": []
    }

    try:
        with open(path, encoding="utf8") as file:
            stored_config = stored_config | yaml.safe_load(file)

    except FileNotFoundError:
        pass

    config_schema.validate(stored_config)

    config = {}

    config["revision"] = stored_config["revision"]
    config["profiles"] = {i["name"]: _to_profile(i) for i in stored_config["profiles"]}
    config["clusters"] = {i["name"]: _to_cluster(i) for i in stored_config["clusters"]}
    config["components"] = {i["name"]: _to_component(i) for i in stored_config["components"]}
    config["links"] = {i["name"]: _to_link(i) for i in stored_config["links"]}

    entry_points = metadata.entry_points()

    if "torque.components" in entry_points:
        config["component_types"] = {i.name: i for i in entry_points["torque.components"]}

    else:
        config["component_types"] = {}

    if "torque.links" in entry_points:
        config["link_types"] = {i.name: i for i in entry_points["torque.links"]}

    else:
        config["link_types"] = {}

    return config


def store(path: str, config: Config):
    """TODO"""

    stored_config = {}

    stored_config["revision"] = config["revision"] + 1

    stored_config["profiles"] = [_from_profile(i) for i in config["profiles"].values()]
    stored_config["clusters"] = [_from_cluster(i) for i in config["clusters"].values()]
    stored_config["components"] = [_from_component(i) for i in config["components"].values()]
    stored_config["links"] = [_from_link(i) for i in config["links"].values()]

    with open(f"{path}.tmp", "w", encoding="utf8") as file:
        yaml.safe_dump(stored_config,
                       stream=file,
                       default_flow_style=False,
                       sort_keys=False)

    os.replace(f"{path}.tmp", path)
