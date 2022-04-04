# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re
import schema
import yaml

from torque import deployment
from torque import exceptions
from torque import extensions
from torque import model
from torque import options
from torque import profile
from torque import utils

from torque.v1 import component as component_v1
from torque.v1 import link as link_v1


_PROTO = r"^([^:]+)://"
_NAME = r"^[A-Za-z_][A-Za-z0-9_]*$"

_WORKSPACE_SCHEMA = schema.Schema({
    "profiles": [{
        "name": str,
        "uri": str,
        "secret": schema.Or(str, None)
    }],
    "config": {
        "default_group": schema.Or(str, None),
        "deployment_config": schema.Or(str, None)
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

_DEPLOYMENTS_SCHEMA = schema.Schema({
    "deployments": [{
        "name": str,
        "profile": str,
        "groups": schema.Or([str], None),
        "components": schema.Or([str], None)
    }]
})


class Profile:
    """TODO"""

    def __init__(self, name: str, uri: str, secret: str):
        self.name = name
        self.uri = uri
        self.secret = secret

    def __repr__(self) -> str:
        return f"Profile({self.name}, uri={self.uri}, secret={self.secret})"


class Deployment:
    """TODO"""

    def __init__(self, name: str, profile: str, groups: list[str], components: list[str]):
        self.name = name
        self.profile = profile
        self.groups = groups
        self.components = components

    def __repr__(self) -> str:
        return \
            f"Deployment({self.name}, profile={self.profile}" \
            f", groups={self.groups}, components={self.components})"


class Configuration:
    """TODO"""

    def __init__(self,
                 default_group: str,
                 deployment_config: str):
        self.default_group = default_group
        self.deployment_config = deployment_config


def _to_profile(profile_workspace: dict[str, object]) -> Profile:
    """TODO"""

    return Profile(profile_workspace["name"],
                   profile_workspace["uri"],
                   profile_workspace["secret"])


def _to_config(config_workspace: dict[str, str]) -> Configuration:
    """TODO"""

    return Configuration(config_workspace["default_group"],
                         config_workspace["deployment_config"])


def _to_deployment(deployment: dict[str, object]) -> Deployment:
    """TODO"""

    return Deployment(deployment["name"],
                      deployment["profile"],
                      deployment["groups"],
                      deployment["components"])


def _to_deployments(deployments: list[dict[str, object]]) -> dict[str, Deployment]:
    """TODO"""

    return {
        i["name"]: _to_deployment(i) for i in deployments
    }


def _from_profile(profile: Profile) -> dict[str, object]:
    """TODO"""

    return {
        "name": profile.name,
        "uri": profile.uri,
        "secret": profile.secret
    }


def _from_profiles(profiles: dict[str, Profile]) -> list[dict[str, object]]:
    """TODO"""

    return [_from_profile(i) for i in profiles.values()]


def _from_config(config: Configuration) -> dict[str, str]:
    """TODO"""

    return {
        "default_group": config.default_group,
        "deployment_config": config.deployment_config
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


def _from_deployment(deployment: Deployment) -> dict[str, object]:
    """TODO"""

    return {
        "name": deployment.name,
        "profile": deployment.profile,
        "groups": deployment.groups,
        "components": deployment.components
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


class Workspace:
    """TODO"""

    def __init__(self,
                 path: str,
                 profiles: dict[str, Profile],
                 config: Configuration,
                 dag: model.DAG,
                 exts: extensions.Extensions,
                 deployments: dict[str, Deployment]):
        # pylint: disable=R0913

        self.path = path
        self.profiles = profiles
        self.config = config
        self.dag = dag
        self.exts = exts
        self.deployments = deployments

    def _create_component(self,
                          component: model.Component,
                          config: options.Options) -> component_v1.Component:
        """TODO"""

        component_type = self.exts.component(component.type)

        return component_type(component.name,
                              component.group,
                              component.params,
                              config)

    def _create_link(self,
                     link: model.Link,
                     config: options.Options,
                     source: component_v1.Component,
                     destination: component_v1.Component) -> link_v1.Link:
        """TODO"""

        link_type = self.exts.link(link.type)

        return link_type(link.name, link.params, config, source, destination)

    def _collect_components(self, groups: list[str], components: list[str]) -> list[str]:
        """TODO"""

        if groups is None and components is None:
            return None

        collected_components = set()

        for group in groups or []:
            if group not in self.dag.groups:
                print(f"WARNING: {group}: group not found")

            else:
                for component in self.dag.components.values():
                    if component.group != group:
                        continue

                    collected_components.add(component.name)

        for component in components or []:
            if component in self.dag.components:
                collected_components.add(component)

            else:
                print(f"WARNING: {component}: component not found")

        return list(collected_components)

    def _load_deployment(self,
                         name: str,
                         components: list[str],
                         profile: profile.Profile) -> deployment.Deployment:
        """TODO"""

        return deployment.load(name, components, profile, self.dag, self.exts)

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

    def load_profile(self, name: str) -> profile.Profile:
        """TODO"""

        if name not in self.profiles:
            raise exceptions.ProfileNotFound(name)

        p = self.profiles[name]

        return profile.load(p.uri, p.secret, self.exts)

    def profile_defaults(self, provider: str) -> dict[str, object]:
        """TODO"""

        return profile.defaults(provider, self.dag, self.exts)

    def create_deployment(self,
                          name: str,
                          profile: str,
                          groups: list[str],
                          components: list[str]) -> Deployment:
        """TODO"""

        if name in self.deployments:
            raise exceptions.DeploymentExists(name)

        if profile not in self.profiles:
            raise exceptions.ProfileNotFound(profile)

        for group in groups or []:
            if group not in self.dag.groups:
                raise exceptions.GroupNotFound(group)

        for component in components or []:
            if component not in self.dag.components:
                raise exceptions.ComponentNotFound(component)

        deployment = Deployment(name, profile, groups, components)

        self.deployments[name] = deployment
        return deployment

    def remove_deployment(self, name: str) -> Deployment:
        """TODO"""

        if name not in self.deployments:
            raise exceptions.DeploymentNotFound(name)

        return self.deployments.pop(name)

    def load_deployment(self, name: str) -> deployment.Deployment:
        """TODO"""

        if name not in self.deployments:
            raise exceptions.DeploymentNotFound(name)

        deployment = self.deployments[name]
        components = self._collect_components(deployment.groups, deployment.components)
        profile = self.load_profile(deployment.profile)

        return self._load_deployment(name, components, profile)

    def create_group(self, name: str, set_default: bool):
        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

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

    def create_component(self,
                         name: str,
                         group: str,
                         type: str,
                         raw_params: options.RawOptions) -> model.Component:
        # pylint: disable=W0622

        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        component_type = self.exts.component(type)
        params = options.process(component_type.parameters(), raw_params)

        for default in params.defaults:
            print(f"WARNING: {default}: used default value")

        for unused in params.unused:
            print(f"WARNING: {unused}: unused parameter")

        component = self.dag.create_component(name, group, type, params)

        instance = self._create_component(component, None)
        instance.on_create()

        self.dag.revision += 1

        return component

    def remove_component(self, name: str) -> model.Component:
        """TODO"""

        component = self.dag.remove_component(name)

        instance = self._create_component(component, None)
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

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        link_type = self.exts.link(type)
        params = options.process(link_type.parameters(), raw_params)

        for default in params.defaults:
            print(f"WARNING: {default}: used default value")

        for unused in params.unused:
            print(f"WARNING: {unused}: unused parameter")

        link = self.dag.create_link(name, source, destination, type, params)

        self.dag.verify()

        source = self._create_component(self.dag.components[link.source], None)
        destination = self._create_component(self.dag.components[link.destination], None)

        instance = self._create_link(link, None, source, destination)
        instance.on_create()

        self.dag.revision += 1

        return link

    def remove_link(self, name: str) -> model.Link:
        """TODO"""

        link = self.dag.remove_link(name)

        source = self._create_component(self.dag.components[link.source], None)
        destination = self._create_component(self.dag.components[link.destination], None)

        instance = self._create_link(link, None, source, destination)
        instance.on_remove()

        self.dag.revision += 1

        return link

    def _store_workspace(self):
        """TODO"""

        workspace = {
            "profiles": _from_profiles(self.profiles),
            "config": _from_config(self.config),
            "dag": {
                "revision": self.dag.revision,
                "groups": [
                    _from_group(i) for i in self.dag.groups.values()
                ],
                "components": [
                    _from_component(i) for i in self.dag.components.values()
                ],
                "links": [
                    _from_link(i) for i in self.dag.links.values()
                ]
            }
        }

        with open(f"{self.path}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(workspace,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self.path}.tmp", self.path)

    def _store_deployments(self):
        """TODO"""

        deployments = {
            "deployments": [
                _from_deployment(i) for i in self.deployments.values()
            ]
        }

        with open(f"{self.config.deployment_config}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(deployments,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self.config.deployment_config}.tmp", self.config.deployment_config)

    def store(self):
        """TODO"""

        self._store_workspace()
        self._store_deployments()


def load(path: str) -> Workspace:
    """TODO"""

    workspace = {
        "profiles": [],
        "config": {
            "default_group": None,
            "deployment_config": ".torque/local/deployments.yaml"
        },
        "dag": {
            "revision": 0,
            "groups": [],
            "components": [],
            "links": []
        }
    }

    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            workspace = utils.merge_dicts(workspace, yaml.safe_load(file))

    workspace = _WORKSPACE_SCHEMA.validate(workspace)
    exts = extensions.load()

    profiles = {
        i["name"]: _to_profile(i) for i in workspace["profiles"]
    }

    config = _to_config(workspace["config"])
    dag = _generate_dag(workspace["dag"], exts)

    deployments = {
        "deployments": []
    }

    if os.path.exists(config.deployment_config):
        with open(config.deployment_config, encoding="utf8") as file:
            deployments = utils.merge_dicts(deployments, yaml.safe_load(file))

    deployments = _to_deployments(deployments["deployments"])

    return Workspace(path, profiles, config, dag, exts, deployments)
