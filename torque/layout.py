# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import importlib
import os
import schema
import yaml

from torque import configuration
from torque import internal
from torque import model


_LAYOUT_SCHEMA = schema.Schema({
    "profiles": [{
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


class Profile:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str, uri: str, secret: str, types: model.Types):
        self.name = name
        self.uri = uri
        self.secret = secret

        self.types = types

    def load(self) -> configuration.Configuration:
        """TODO"""

        return configuration.load(self.uri, self.secret, self.types)


Profiles = dict[str, Profile]


def _to_profile(profile_layout: dict[str, object], types: model.Types) -> Profile:
    """TODO"""

    return Profile(profile_layout["name"],
                   profile_layout["uri"],
                   profile_layout["secret"],
                   types)


def _from_profile(profile: Profile) -> dict[str, object]:
    """TODO"""

    return {
        "name": profile.name,
        "uri": profile.uri,
        "secret": profile.secret
    }

def _from_profiles(profiles: Profiles) -> list[dict[str, object]]:
    """TODO"""

    return [_from_profile(i) for i in profiles.values()]


def _from_cluster(cluster: model.Cluster) -> dict[str: str]:
    """TODO"""

    return {
        "name": cluster.name
    }


def _from_params(params: dict[str, str]) -> list[dict[str, str]]:
    """TODO"""

    return [
        {"name": name, "value": value} for name, value in params.raw.items()
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


def _load_types(extra_types: model.Types):
    """TODO"""

    types = {} | internal.TYPES

    entry_points = importlib.metadata.entry_points()

    if "torque.components.v1" in entry_points:
        for i in entry_points["torque.components.v1"]:
            # pylint: disable=W0703
            try:
                types["components.v1"][i.name] = i.load()

            except Exception as exc:
                print(f"WARNING: {i.name}: unable to load type: {exc}")

    if "torque.links.v1" in entry_points:
        for i in entry_points["torque.links.v1"]:
            # pylint: disable=W0703
            try:
                types["links.v1"][i.name] = i.load()

            except Exception as exc:
                print(f"WARNING: {i.name}: unable to load type: {exc}")

    if extra_types:
        types = types | extra_types

    return types


def load(path: str, extra_types: model.Types = None) -> (model.DAG, Profiles):
    """TODO"""

    layout = {
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
            layout = layout | yaml.safe_load(file)

    except FileNotFoundError:
        pass

    _LAYOUT_SCHEMA.validate(layout)

    types = _load_types(extra_types)

    profiles = {
        i["name"]: _to_profile(i, types) for i in layout["profiles"]
    }

    dag = _generate_dag(layout["dag"], types)

    return dag, profiles


def store(path: str, dag: model.DAG, profiles: Profiles):
    """TODO"""

    layout = {
        "profiles": [],
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

    layout["profiles"] = _from_profiles(profiles)

    with open(f"{path}.tmp", "w", encoding="utf8") as file:
        yaml.safe_dump(layout,
                       stream=file,
                       default_flow_style=False,
                       sort_keys=False)

    os.replace(f"{path}.tmp", path)
