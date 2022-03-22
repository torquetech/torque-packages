# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re
import schema
import yaml

from torque import configuration
from torque import exceptions
from torque import extensions
from torque import model
from torque import options

from torque.v1 import interfaces


_PROTO = r"^([^:]+)://"
_WORKSPACE_SCHEMA = schema.Schema({
    "profiles": [{
        "name": str,
        "uri": str,
        "secret": schema.Or(str, None)
    }],
    "config": {
        "default_group": schema.Or(str, None)
    },
    "dag": {
        "revision": int,
        "groups": [{
            "name": str
        }],
        "components": [{
            "name": str,
            "group": str,
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


class Config:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, default_group: str):
        self.default_group = default_group


def _to_profile(profile_workspace: dict[str, object]) -> Profile:
    """TODO"""

    return Profile(profile_workspace["name"],
                   profile_workspace["uri"],
                   profile_workspace["secret"])


def _to_config(config_workspace: dict[str, str]) -> Config:
    """TODO"""

    return Config(config_workspace["default_group"])


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


def _from_config(config: Config) -> dict[str, str]:
    """TODO"""

    return {
        "default_group": config.default_group
    }


def _from_group(group: model.Group) -> dict[str: str]:
    """TODO"""

    return {
        "name": group.name
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
        "group": component.group,
        "type": component.type,
        "params": _from_params(component.params)
    }


def _from_link(link: model.Link) -> dict[str: object]:
    """TODO"""

    return {
        "name": link.name,
        "source": link.source,
        "destination": link.destination,
        "type": link.type,
        "params": _from_params(link.params)
    }


def _generate_dag(dag_workspace: dict[str, object], exts: extensions.Extensions) -> model.DAG:
    """TODO"""

    dag = model.DAG(dag_workspace["revision"])

    for group in dag_workspace["groups"]:
        dag.create_group(group["name"])

    for component in dag_workspace["components"]:
        raw_params = {i["name"]: i["value"] for i in component["params"]}

        component_type = exts.component(component["type"])
        params = options.process(component_type.parameters(), raw_params)

        dag.create_component(component["name"],
                             component["group"],
                             component["type"],
                             params)

    for link in dag_workspace["links"]:
        raw_params = {i["name"]: i["value"] for i in link["params"]}

        link_type = exts.link(link["type"])
        params = options.process(link_type.parameters(), raw_params)

        dag.create_link(link["name"],
                        link["source"],
                        link["destination"],
                        link["type"],
                        params)

    dag.verify()

    return dag


def _load_defaults(dag: model.DAG, exts: extensions.Extensions) -> configuration.Configuration:
    """TODO"""

    config = {
        "providers": [],
        "dag": {
            "revision": dag.revision,
            "groups": [],
            "components": [],
            "links": []
        }
    }

    groups = config["dag"]["groups"]
    components = config["dag"]["components"]
    links = config["dag"]["links"]

    for group in dag.groups.values():
        groups.append({"name": group.name, "configuration": []})

    for component in dag.components.values():
        component_type = exts.component(component.type)
        components.append({
            "name": component.name,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in component_type.configuration()
            ]
        })

    for link in dag.links.values():
        link_type = exts.link(link.type)
        links.append({
            "name": link.name,
            "configuration": [
                {"name": i.name, "value": i.default_value} for i in link_type.configuration()
            ]
        })

    return configuration.create(config, True)


def _store(path: str, profiles: Profiles, config: Config, dag: model.DAG):
    """TODO"""

    workspace = {
        "profiles": [],
        "config": {
            "default_group": None
        },
        "dag": {
            "revision": 0,
            "groups": [],
            "components": [],
            "links": []
        }
    }

    workspace["profiles"] = _from_profiles(profiles)
    workspace["config"] = _from_config(config)

    dag_workspace = workspace["dag"]

    dag_workspace["revision"] = dag.revision
    dag_workspace["groups"] = [_from_group(i) for i in dag.groups.values()]
    dag_workspace["components"] = [_from_component(i) for i in dag.components.values()]
    dag_workspace["links"] = [_from_link(i) for i in dag.links.values()]

    with open(f"{path}.tmp", "w", encoding="utf8") as file:
        yaml.safe_dump(workspace,
                       stream=file,
                       default_flow_style=False,
                       sort_keys=False)

    os.replace(f"{path}.tmp", path)


class Workspace:
    """TODO"""

    def __init__(self,
                 path: str,
                 profiles: Profiles,
                 config: Config,
                 dag: model.DAG,
                 exts: extensions.Extensions):
        # pylint: disable=R0913

        self.path = path
        self.profiles = profiles
        self.config = config
        self.dag = dag
        self.exts = exts

    def _component_instance(self, component: model.Component, config: options.Options) -> interfaces.Component:
        """TODO"""

        component_type = self.exts.component(component.type)

        return component_type(component.name, component.group, component.params, config)

    def _link_instance(self,
                       link: model.Link,
                       config: options.Options,
                       source: interfaces.Component,
                       destination: interfaces.Component) -> interfaces.Link:
        """TODO"""

        link_type = self.exts.link(link.type)

        return link_type(link.name, link.params, config, source, destination)

    def _initialize_dsl(self):
        """TODO"""

        if hasattr(interfaces.DSL, '_initialized'):
            return

        for ext_name, ext in self.exts.dsl_extensions().items():
            for name, cls in ext.items():
                if hasattr(interfaces.DSL, name):
                    raise exceptions.DuplicateDSLEntry(ext_name, name)

                setattr(interfaces.DSL, name, cls)

        setattr(interfaces.DSL, '_initialized', True)

    def load_dsl(self) -> interfaces.DSL:
        """TODO"""

        self._initialize_dsl()
        return interfaces.DSL()

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
            return _load_defaults(self.dag, self.exts)

        profile = self.profiles[name]

        proto = "file"
        match = re.match(_PROTO, profile.uri)

        if match:
            proto = match[1]

        handler = self.exts.protocol(proto)
        config = None

        with handler(profile.uri, profile.secret) as file:
            config = yaml.safe_load(file)

        return configuration.create(config, False)

    def create_group(self, name: str, set_default: bool):
        """TODO"""

        self.dag.create_group(name)

        if set_default:
            self.config.default_group = name

        self.dag.revision += 1

    def remove_group(self, name: str):
        """TODO"""

        self.dag.remove_group(name)
        self.dag.revision += 1

    def set_default_group(self, name: str):
        """TODO"""

        if not self.dag.has_group(name):
            raise exceptions.GroupNotFound(name)

        self.config.default_group = name

    def create_component(self, name: str, group: str, type: str, raw_params: options.RawOptions) -> model.Component:
        # pylint: disable=W0622

        """TODO"""

        component_type = self.exts.component(type)
        params = options.process(component_type.parameters(), raw_params)

        component = self.dag.create_component(name, group, type, params)

        instance = self._component_instance(component, None)
        instance.on_create()

        self.dag.revision += 1

        return component

    def remove_component(self, name: str) -> model.Component:
        """TODO"""

        component = self.dag.remove_component(name)

        instance = self._component_instance(component, None)
        instance.on_remove()

        self.dag.revision += 1

        return component

    def create_link(self,
                    name: str,
                    source: str,
                    destination: str,
                    type: str,
                    raw_params: options.RawOptions) -> model.Link:
        # pylint: disable=W0622,R0913

        """TODO"""

        link_type = self.exts.link(type)
        params = options.process(link_type.parameters(), raw_params)

        link = self.dag.create_link(name, source, destination, type, params)

        self.dag.verify()

        source = self._component_instance(self.dag.components[link.source], None)
        destination = self._component_instance(self.dag.components[link.destination], None)

        instance = self._link_instance(link, None, source, destination)
        instance.on_create()

        self.dag.revision += 1

        return link

    def remove_link(self, name: str) -> model.Link:
        """TODO"""

        link = self.dag.remove_link(name)

        source = self._component_instance(self.dag.components[link.source], None)
        destination = self._component_instance(self.dag.components[link.destination], None)

        instance = self._link_instance(link, None, source, destination)
        instance.on_remove()

        self.dag.revision += 1

        return link

    def store(self):
        """TODO"""

        _store(self.path, self.profiles, self.config, self.dag)


def load(path: str) -> (model.DAG, Profiles):
    """TODO"""

    workspace = {
        "profiles": [],
        "config": {
            "default_group": None
        },
        "dag": {
            "revision": 0,
            "groups": [],
            "components": [],
            "links": []
        }
    }

    try:
        with open(path, encoding="utf8") as file:
            workspace = workspace | yaml.safe_load(file)

    except FileNotFoundError:
        pass

    workspace = _WORKSPACE_SCHEMA.validate(workspace)
    exts = extensions.load()

    profiles = {
        "default": DefaultProfile()
    }

    profiles = profiles | {
        i["name"]: _to_profile(i) for i in workspace["profiles"]
    }

    config = _to_config(workspace["config"])
    dag = _generate_dag(workspace["dag"], exts)

    return Workspace(path, profiles, config, dag, exts)