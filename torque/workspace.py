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
from torque import model
from torque import profile
from torque import repository

from torque.v1 import component as component_v1
from torque.v1 import link as link_v1
from torque.v1 import utils as utils_v1


_PROTO = r"^([^:]+)://"
_NAME = r"^[A-Za-z_][A-Za-z0-9_]*$"

_WORKSPACE_SCHEMA = schema.Schema({
    "profiles": {
        schema.Optional(str): [str]
    },
    "configuration": {
        "deployments": schema.Or(str, None)
    },
    "dag": {
        "revision": int,
        "components": {
            schema.Optional(str): {
                "labels": [str],
                "type": str,
                "parameters": object
            }
        },
        "links": {
            schema.Optional(str): {
                "source": str,
                "destination": str,
                "type": str,
                "parameters": object
            }
        }
    }
})

_DEPLOYMENTS_SCHEMA = schema.Schema({
    schema.Optional(str): {
        "profile": str,
        "lables": schema.Or([str], None),
        "components": schema.Or([str], None)
    }
})


class Profile:
    """TODO"""

    def __init__(self, name: str, uris: [str]):
        self.name = name
        self.uris = uris

    def __repr__(self) -> str:
        uris = ", ".join(self.uris)
        return f"Profile({self.name}, uris=[{uris}])"


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

    def __init__(self, deployments: str):
        self.deployments = deployments


def _to_profiles(workspace: dict[str, object]) -> Profile:
    """TODO"""

    return {
        name: Profile(name, uris) for name, uris in workspace["profiles"].items()
    }


def _to_configuration(workspace: dict[str, object]) -> Configuration:
    """TODO"""

    config = workspace["configuration"]

    return Configuration(config["deployments"])


def _to_deployments(config: Configuration) -> dict[str, Deployment]:
    """TODO"""

    path = utils_v1.resolve_path(config.deployments)

    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf8") as file:
        deployments = yaml.safe_load(file)

    return {
        name: Deployment(name,
                         deployment["profile"],
                         deployment["labels"],
                         deployment["components"]) for name, deployment in deployments.items()
    }


def _from_profiles(profiles: dict[str, Profile]) -> dict[str, object]:
    """TODO"""

    return {
        profile.name: profile.uris for profile in profiles.values()
    }


def _from_configuration(config: Configuration) -> dict[str, str]:
    """TODO"""

    return {
        "deployments": config.deployments
    }


def _from_components(components: dict[str, model.Component]) -> dict[str: object]:
    """TODO"""

    return {
        component.name: {
            "labels": component.labels,
            "type": component.type,
            "parameters": component.parameters
        } for component in components.values()
    }


def _from_links(links: dict[str, model.Link]) -> dict[str: object]:
    """TODO"""

    return {
        link.name: {
            "source": link.source,
            "destination": link.destination,
            "type": link.type,
            "parameters": link.parameters
        } for link in links.values()
    }


def _from_deployments(deployments: dict[str, Deployment]) -> dict[str, object]:
    """TODO"""

    return {
        deployment.name: {
            "profile": deployment.profile,
            "labels": deployment.labels,
            "components": deployment.components
        } for deployment in deployments.values()
    }


def _generate_dag(workspace: dict[str, object]):
    """TODO"""

    workspace_dag = workspace["dag"]
    dag = model.DAG(workspace_dag["revision"])

    for name, component in workspace_dag["components"].items():
        dag.create_component(name,
                             component["type"],
                             component["labels"],
                             component["parameters"])

    for name, link in workspace_dag["links"].items():
        dag.create_link(name,
                        link["type"],
                        link["source"],
                        link["destination"],
                        link["parameters"])

    dag.verify()

    return dag


class Workspace:
    """TODO"""

    def __init__(self,
                 path: str,
                 profiles: dict[str, Profile],
                 config: Configuration,
                 deployments: dict[str, Deployment],
                 dag: model.DAG,
                 repo: repository.Repository):
        # pylint: disable=R0913

        self.dag = dag
        self.repo = repo
        self.deployments = deployments
        self.profiles = profiles
        self._path = path
        self._config = config

    def _component(self, component: model.Component):
        """TODO"""

        component_type = self.repo.component(component.type)

        return component_type(component.name,
                              component.labels,
                              component.parameters)

    def _link(self,
              link: model.Link,
              source: component_v1.Component,
              destination: component_v1.Component) -> link_v1.Link:
        """TODO"""

        link_type = self.repo.link(link.type)

        return link_type(link.name,
                         link.parameters,
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
                         profile: profile.Profile) -> deployment.Deployment:
        """TODO"""

        return deployment.load(name,
                               components,
                               profile,
                               self.dag,
                               self.repo)

    def create_profile(self, name: str, uris: [str]) -> Profile:
        """TODO"""

        if name in self.profiles:
            raise exceptions.ProfileExists(name)

        _uris = []

        for uri in uris:
            if not re.match(_PROTO, uri):
                uri = utils_v1.torque_path(uri)

            _uris.append(uri)

        profile = Profile(name, _uris)

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

        return profile.load(name, self.profiles[name].uris, self.repo)

    def profile_defaults(self, provider: str) -> dict[str, object]:
        """TODO"""

        return profile.defaults(provider, self.dag, self.repo)

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

        return self._load_deployment(name, components, profile)

    def create_component(self,
                         name: str,
                         type: str,
                         labels: [str],
                         params: object) -> model.Component:
        # pylint: disable=W0622

        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        component_type = self.repo.component(type)

        try:
            params = component_type.validate_parameters(params)

        except RuntimeError as exc:
            raise RuntimeError(f"component: {name}: {exc}") from exc

        component = self.dag.create_component(name, type, labels, params)

        instance = self._component(component)
        instance.on_create()

        self.dag.revision += 1

        return component

    def remove_component(self, name: str) -> model.Component:
        """TODO"""

        component = self.dag.remove_component(name)

        instance = self._component(component)
        instance.on_remove()

        self.dag.revision += 1

        return component

    def create_link(self,
                    name: str,
                    type: str,
                    params: object,
                    source: str,
                    destination: str) -> model.Link:
        # pylint: disable=W0622,R0913

        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        link_type = self.repo.link(type)

        try:
            params = link_type.validate_parameters(params)

        except RuntimeError as exc:
            raise RuntimeError(f"link: {name}: {exc}") from exc

        link = self.dag.create_link(name, type, source, destination, params)

        self.dag.verify()

        source = self._component(self.dag.components[link.source])
        destination = self._component(self.dag.components[link.destination])

        instance = self._link(link, source, destination)
        instance.on_create()

        self.dag.revision += 1

        return link

    def remove_link(self, name: str) -> model.Link:
        """TODO"""

        link = self.dag.remove_link(name)

        source = self._component(self.dag.components[link.source])
        destination = self._component(self.dag.components[link.destination])

        instance = self._link(link, source, destination)
        instance.on_remove()

        self.dag.revision += 1

        return link

    def _store_workspace(self):
        """TODO"""

        workspace = {
            "profiles": _from_profiles(self.profiles),
            "configuration": _from_configuration(self._config),
            "dag": {
                "revision": self.dag.revision,
                "components": _from_components(self.dag.components),
                "links": _from_links(self.dag.links)
            }
        }

        with open(f"{self._path}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(workspace,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self._path}.tmp", self._path)

    def _store_deployments(self):
        """TODO"""

        path = utils_v1.resolve_path(self._config.deployments)

        with open(f"{path}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(_from_deployments(self.deployments),
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{path}.tmp", path)

    def store(self):
        """TODO"""

        self._store_workspace()
        self._store_deployments()


def load(path: str) -> Workspace:
    """TODO"""

    path = utils_v1.torque_path(path)
    path = utils_v1.resolve_path(path)

    workspace = {
        "profiles": {},
        "configuration": {
            "deployments": ".torque/local/deployments.yaml"
        },
        "dag": {
            "revision": 0,
            "components": {},
            "links": {}
        }
    }

    if os.path.exists(path):
        with open(path, encoding="utf8") as file:
            workspace = utils_v1.merge_dicts(workspace, yaml.safe_load(file))

    workspace = _WORKSPACE_SCHEMA.validate(workspace)
    repo = repository.load()

    profiles = _to_profiles(workspace)
    configuration = _to_configuration(workspace)
    deployments = _to_deployments(configuration)

    dag = _generate_dag(workspace)

    return Workspace(path, profiles, configuration, deployments, dag, repo)


def _load_params(path: str) -> object:
    """TODO"""

    if not path:
        return {}

    if path == "-":
        params = sys.stdin.read()

    else:
        with open(path, encoding="utf8") as file:
            params = file.read()

    return yaml.safe_load(params)


def process_parameters(path: str, params: [str]) -> object:
    """TODO"""

    _params = _load_params(path)

    if not params:
        return _params

    for p in params:
        ndx = p.index("=")

        name = p[:ndx]
        value = p[ndx+1:]

        _params[name] = value

    return _params
