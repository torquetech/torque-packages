# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import importlib
import os
import re
import schema
import yaml

from torque import configuration
from torque import exceptions
from torque import interface
from torque import model
from torque import options


def _proto_file(uri: str, secret: str) -> dict[str, object]:
    # pylint: disable=W0613

    """TODO"""

    return open(uri, encoding="utf8")


_TYPES = {
    "protocols.v1": {
        "file": _proto_file,
        # "https": _proto_https
        # "http": _proto_http
    },
    "components.v1": {},
    "links.v1": {}
}


_PROTO = r"^([^:]+)://"
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


class DefaultProfile:
    # pylint: disable=R0903

    """TODO"""

    def __repr__(self) -> str:
        return "Profile(default)"


class Profile:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str, uri: str, secret: str):
        self.name = name
        self.uri = uri
        self.secret = secret

    def __repr__(self) -> str:
        return f"Profile({self.name}, uri={self.uri}, secret={self.secret})"


Profiles = dict[str, Profile]


class Types:
    """TODO"""

    def __init__(self, types: dict[str, object]):
        self.types = types

    def component(self, component_type: str) -> interface.Component:
        """TODO"""

        components = self.types["components.v1"]

        if component_type not in components:
            raise exceptions.ComponentTypeNotFound(component_type)

        return components[component_type]

    def link(self, link_type: str) -> interface.Link:
        """TODO"""

        links = self.types["links.v1"]

        if link_type not in links:
            raise exceptions.LinkTypeNotFound(link_type)

        return links[link_type]

    def proto(self, protocol: str) -> callable:
        """TODO"""

        protocols = self.types["protocols.v1"]

        if protocol not in protocols:
            raise exceptions.ProtocolNotFound(protocol)

        return protocols[protocol]


def _to_profile(profile_layout: dict[str, object]) -> Profile:
    """TODO"""

    return Profile(profile_layout["name"],
                   profile_layout["uri"],
                   profile_layout["secret"])


def _from_profile(profile: Profile) -> dict[str, object]:
    """TODO"""

    return {
        "name": profile.name,
        "uri": profile.uri,
        "secret": profile.secret
    }


def _from_profiles(profiles: Profiles) -> list[dict[str, object]]:
    """TODO"""

    profile_list = filter(lambda x: not isinstance(x, DefaultProfile), profiles.values())

    return [_from_profile(i) for i in profile_list]


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


def _load_types_for(source: str) -> dict[str, object]:
    """TODO"""

    entry_points = importlib.metadata.entry_points()

    if source not in entry_points:
        return {}

    types = {}

    for i in entry_points[source]:
        # pylint: disable=W0703
        try:
            types[i.name] = i.load()

        except Exception as exc:
            print(f"WARNING: {i.name}: unable to load type: {exc}")

    return types


def _load_types():
    """TODO"""

    types = {} | _TYPES

    types["components.v1"] |= _load_types_for("torque.components.v1")
    types["links.v1"] |= _load_types_for("torque.links.v1")
    types["protocols.v1"] |= _load_types_for("torque.protocols.v1")

    return types


def _generate_dag(dag_layout: dict[str, object], types: Types) -> model.DAG:
    """TODO"""

    dag = model.DAG(dag_layout["revision"])

    for cluster in dag_layout["clusters"]:
        dag.create_cluster(cluster["name"])

    for component in dag_layout["components"]:
        raw_params = {i["name"]: i["value"] for i in component["params"]}

        component_type = types.component(component["type"])
        params = options.process(component_type.parameters, raw_params)

        dag.create_component(component["name"],
                             component["cluster"],
                             component["type"],
                             params)

    for link in dag_layout["links"]:
        raw_params = {i["name"]: i["value"] for i in link["params"]}

        link_type = types.link(link["type"])
        params = options.process(link_type.parameters, raw_params)

        dag.create_link(link["name"],
                        link["source"],
                        link["destination"],
                        link["type"],
                        params)

    dag.verify()

    return dag


def _load_defaults(dag: model.DAG, types: Types) -> configuration.Configuration:
    """TODO"""

    config = {
        "providers": [],
        "dag": {
            "revision": dag.revision,
            "clusters": [],
            "components": [],
            "links": []
        }
    }

    clusters = config["dag"]["clusters"]
    components = config["dag"]["components"]
    links = config["dag"]["links"]

    for cluster in dag.clusters.values():
        clusters.append({"name": cluster.name, "configuration": []})

    for component in dag.components.values():
        component_type = types.component(component.component_type)
        components.append({
            "name": component.name,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in component_type.configuration
            ]
        })

    for link in dag.links.values():
        link_type = types.link(link.link_type)
        links.append({
            "name": link.name,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in link_type.configuration
            ]
        })

    return configuration.create(config, True)


def _store(path: str, dag: model.DAG, profiles: Profiles):
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

    dag_layout["revision"] = dag.revision
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


class Layout:
    """TODO"""

    def __init__(self, path: str, dag: model.DAG, profiles: Profiles, types: Types):
        self.path = path
        self.dag = dag
        self.profiles = profiles
        self.types = types

    def create_profile(self, name: str, uri: str, secret: str) -> Profile:
        """TODO"""

        if name in self.profiles:
            raise exceptions.ProfileExists(name)

        if not re.match(_PROTO, uri) and not os.path.isabs(uri):
            uri = os.path.join(os.getenv("TORQUE_CWD"), uri)
            uri = os.path.abspath(uri)
            uri = os.path.relpath(uri)

        profile = Profile(name, uri, secret)

        self.profiles[name] = profile
        return profile

    def remove_profile(self, name: str) -> Profile:
        """TODO"""

        if name not in self.profiles:
            raise exceptions.ProfileNotFound(name)

        return self.profiles.pop(name)

    def load_profile(self, name: str) -> configuration.Configuration:
        """TODO"""

        if name not in self.profiles:
            raise exceptions.ProfileNotFound(name)

        if name == "default":
            return _load_defaults(self.dag, self.types)

        profile = self.profiles[name]

        proto = "file"
        match = re.match(_PROTO, profile.uri)

        if match:
            proto = match[1]

        handler = self.types.proto(proto)
        config = None

        with handler(profile.uri, profile.secret) as file:
            config = yaml.safe_load(file)

        return configuration.create(config, False)

    def store(self):
        """TODO"""

        _store(self.path, self.dag, self.profiles)


def load(path: str, extra_types: dict[str, object] = None) -> (model.DAG, Profiles):
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

    types = _load_types()

    if extra_types:
        types = types | extra_types

    types = Types(types)

    profiles = {
        "default": DefaultProfile()
    }

    profiles = profiles | {
        i["name"]: _to_profile(i) for i in layout["profiles"]
    }

    dag = _generate_dag(layout["dag"], types)

    return Layout(path, dag, profiles, types)
