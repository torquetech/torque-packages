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


Configuration = namedtuple("Option", ["name", "uri", "secret"])
Configurations = dict[str, Configuration]


_LAYOUT_SCHEMA = schema.Schema({
    "configurations": [{
        "name": str,
        "uri": str,
        "secret": schema.Or(str, None)
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


def _to_config(config: dict[str, object]) -> Configuration:
    """TODO"""

    return Configuration(config["name"],
                         config["uri"],
                         config["secret"])


def _from_configs(configs: Configurations) -> list[dict[str, object]]:
    """TODO"""

    return [
        {"name": i.name, "uri": i.uri, "secret": i.secret} for i in configs.values()
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


def _generate_dag(dag_layout: dict[str, object], types: model.Types) -> model.DAG:
    """TODO"""

    dag = model.DAG(dag_layout["revision"], types)

    for cluster in dag_layout["clusters"]:
        dag.create_cluster(cluster["name"])

    for component in dag_layout["components"]:
        params = {i["name"]: i["value"] for i in component["params"]}

        dag.create_component(component["name"],
                             component["cluster"],
                             component["type"],
                             params)

    for link in dag_layout["links"]:
        params = {i["name"]: i["value"] for i in link["params"]}

        dag.create_link(link["name"],
                        link["source"],
                        link["destination"],
                        link["type"],
                        params)

    dag.verify()

    return dag


def load(path: str, extra_types: model.Types = None) -> (model.DAG, Configurations):
    """TODO"""

    layout = {
        "configurations": [],
        "dag": {
            "revision": 0,
            "clusters": [],
            "components": [],
            "links": []
        }
    }

    try:
        with open(path, encoding="utf8") as file:
            layout = layout | yaml.safe_load(file)

    except FileNotFoundError:
        pass

    _LAYOUT_SCHEMA.validate(layout)

    configs = {i["name"]: _to_config(i) for i in layout["configurations"]}
    types = {}

    entry_points = metadata.entry_points()

    types["components.v1"] = {}

    if "torque.components.v1" in entry_points:
        for i in entry_points["torque.components.v1"]:
            # pylint: disable=W0703
            try:
                types["components.v1"][i.name] = i.load()

            except Exception as exc:
                print(f"WARNING: {i.name}: unable to load type: {exc}")

    types["links.v1"] = {}

    if "torque.links.v1" in entry_points:
        for i in entry_points["torque.links.v1"]:
            # pylint: disable=W0703
            try:
                types["links.v1"][i.name] = i.load()

            except Exception as exc:
                print(f"WARNING: {i.name}: unable to load type: {exc}")

    if extra_types:
        types = types | extra_types

    dag = _generate_dag(layout["dag"], types)

    return dag, configs


def store(path: str, dag: model.DAG, configs: Configurations):
    """TODO"""

    layout = {
        "configurations": [],
        "dag": {
            "revision": 0,
            "clusters": [],
            "components": [],
            "links": []
        }
    }

    dag_layout = layout["dag"]

    dag_layout["revision"] = dag.revision + 1
    dag_layout["clusters"] = [_from_cluster(i) for i in dag.clusters.values()]
    dag_layout["components"] = [_from_component(i) for i in dag.components.values()]
    dag_layout["links"] = [_from_link(i) for i in dag.links.values()]

    layout["configurations"] = _from_configs(configs)

    with open(f"{path}.tmp", "w", encoding="utf8") as file:
        yaml.safe_dump(layout,
                       stream=file,
                       default_flow_style=False,
                       sort_keys=False)

    os.replace(f"{path}.tmp", path)
