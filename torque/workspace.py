# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re
import sys

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
        "deployment": schema.Or(str, None)
    },
    "dag": {
        "revision": int,
        "components": [{
            "name": str,
            "labels": [str],
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
        "lables": schema.Or([str], None),
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

    def __init__(self, name: str, profile: str, labels: [str], components: [str]):
        self.name = name
        self.profile = profile
        self.labels = labels
        self.components = components

    def __repr__(self) -> str:
        return \
            f"Deployment({self.name}, profile={self.profile}" \
            f", labels={self.labels}, components={self.components})"


class Configuration:
    """TODO"""

    def __init__(self, deployment: str):
        self.deployment = deployment


def _to_profile(profile_workspace: dict[str, object]) -> Profile:
    """TODO"""

    return Profile(profile_workspace["name"],
                   profile_workspace["uri"],
                   profile_workspace["secret"])


def _to_config(config_workspace: dict[str, str]) -> Configuration:
    """TODO"""

    return Configuration(config_workspace["deployment"])


def _to_deployment(deployment: dict[str, object]) -> Deployment:
    """TODO"""

    return Deployment(deployment["name"],
                      deployment["profile"],
                      deployment["labels"],
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
        "deployment": config.deployment
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
        "labels": component.labels,
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
        "labels": deployment.labels,
        "components": deployment.components
    }


def _generate_dag(dag_workspace: dict[str, object], exts: extensions.Extensions) -> model.DAG:
    """TODO"""

    dag = model.DAG(dag_workspace["revision"])

    for component in dag_workspace["components"]:
        raw_params = {i["name"]: i["value"] for i in component["params"]}

        component_type = exts.component(component["type"])
        params = options.process(component_type.parameters(), raw_params)

        dag.create_component(component["name"],
                             component["type"],
                             component["labels"],
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


def _process_params(params: [str]) -> options.RawOptions:
    """TODO"""

    if not params:
        return {}

    params = [i.split("=") for i in params]
    params = {i[0]: "".join(i[1:]) for i in params}

    return params


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

        if config:
            config = config.processed

        component_type = self.exts.component(component.type)

        return component_type(component.name,
                              component.labels,
                              component.params.processed,
                              config)

    def _create_link(self,
                     link: model.Link,
                     config: options.Options,
                     source: component_v1.Component,
                     destination: component_v1.Component) -> link_v1.Link:
        """TODO"""

        if config:
            config = config.processed

        link_type = self.exts.link(link.type)

        return link_type(link.name,
                         link.params.processed,
                         config,
                         source,
                         destination)

    def _collect_components(self, labels: [str], components: [str]) -> [str]:
        """TODO"""

        if labels is None and components is None:
            return None

        labels = set(labels or [])
        components = set(components or [])

        collected_components = set()

        for component in self.dag.components.values():
            if labels.intersection(component.labels):
                collected_components.add(component.name)

            if component.name in components:
                collected_components.add(component.name)

        return list(collected_components)

    def _load_deployment(self,
                         name: str,
                         components: [str],
                         profile_name: str,
                         profile: profile.Profile) -> deployment.Deployment:
        """TODO"""

        return deployment.load(name,
                               components,
                               profile_name,
                               profile,
                               self.dag,
                               self.exts)

    def create_profile(self, name: str, uri: str, secret: str) -> Profile:
        """TODO"""

        if name in self.profiles:
            raise exceptions.ProfileExists(name)

        if not re.match(_PROTO, uri):
            uri = utils.torque_path(uri)

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
                          labels: [str],
                          components: [str]) -> Deployment:
        """TODO"""

        if name in self.deployments:
            raise exceptions.DeploymentExists(name)

        if profile not in self.profiles:
            raise exceptions.ProfileNotFound(profile)

        for component in components or []:
            if component not in self.dag.components:
                raise exceptions.ComponentNotFound(component)

        deployment = Deployment(name, profile, labels, components)

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
        components = self._collect_components(deployment.labels, deployment.components)
        profile = self.load_profile(deployment.profile)

        return self._load_deployment(name, components, deployment.profile, profile)

    def create_component(self,
                         name: str,
                         type: str,
                         labels: [str],
                         params: [str]) -> model.Component:
        # pylint: disable=W0622

        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        component_type = self.exts.component(type)

        params = _process_params(params)
        params = options.process(component_type.parameters(), params)

        for default in params.defaults:
            print(f"WARNING: {default}: used default value", file=sys.stderr)

        for unused in params.unused:
            print(f"WARNING: {unused}: unused parameter", file=sys.stderr)

        component = self.dag.create_component(name, type, labels, params)

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
                    params: [str]) -> model.Link:
        # pylint: disable=W0622,R0913

        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        link_type = self.exts.link(type)

        params = _process_params(params)
        params = options.process(link_type.parameters(), params)

        for default in params.defaults:
            print(f"WARNING: {default}: used default value", file=sys.stderr)

        for unused in params.unused:
            print(f"WARNING: {unused}: unused parameter", file=sys.stderr)

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

        deployment = utils.resolve_path(self.config.deployment)

        with open(f"{deployment}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(deployments,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{deployment}.tmp", deployment)

    def store(self):
        """TODO"""

        self._store_workspace()
        self._store_deployments()


def load(path: str) -> Workspace:
    """TODO"""

    path = utils.torque_path(path)
    path = utils.resolve_path(path)

    workspace = {
        "profiles": [],
        "config": {
            "deployment": ".torque/local/deployments.yaml"
        },
        "dag": {
            "revision": 0,
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

    deployment = utils.resolve_path(config.deployment)

    if os.path.exists(deployment):
        with open(deployment, encoding="utf8") as file:
            deployments = utils.merge_dicts(deployments, yaml.safe_load(file))

    deployments = _to_deployments(deployments["deployments"])

    return Workspace(path, profiles, config, dag, exts, deployments)
