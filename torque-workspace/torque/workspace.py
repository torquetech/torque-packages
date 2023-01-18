# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os
import re

import pytrie
import yaml

from torque import dag
from torque import deployment
from torque import exceptions
from torque import interfaces
from torque import repository
from torque import v1


_NAME = re.compile(r"^[a-z-][a-z0-9-]*$")
_KEY = re.compile(r"^[a-z0-9.\-_/]+$")

_MAX_DEPLOYMENT_NAME_LENGTH = 16
_MAX_COMPONENT_NAME_LENGTH = 32
_MAX_LINK_NAME_LENGTH = 32

_WORKSPACE_SCHEMA = v1.schema.Schema({
    "version": str,
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): {
                "type": str,
                "parameters": dict,
                "labels": [str]
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "type": str,
                "source": str,
                "destination": str,
                "parameters": dict,
                "labels": [str]
            }
        }
    }
})

_DEPLOYMENTS_SCHEMA = v1.schema.Schema({
    "version": str,
    "deployments": {
        v1.schema.Optional(str): {
            "context": {
                "type": str,
                "configuration": dict
            },
            "strict": bool,
            "providers": [str],
            "extra_configuration": [str],
            "filters": v1.schema.Or([str], None),
            "components": v1.schema.Or([str], None)
        }
    }
})


class Deployment:
    """DOCSTRING"""

    def __init__(self,
                 name: str,
                 context_type: str,
                 context_config: dict[str, object],
                 strict: bool,
                 providers: str,
                 extra_configs: [str],
                 filters: [str],
                 components: [str]):
        self.name = name
        self.context_type = context_type
        self.context_config = context_config
        self.strict = strict
        self.providers = providers
        self.extra_configs = extra_configs
        self.filters = filters
        self.components = components

    def describe(self) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "name": self.name,
            "context": {
                "type": self.context_type,
                "configuration": self.context_config
            },
            "strict": self.strict,
            "providers": self.providers,
            "extra_configs": self.extra_configs,
            "filters": self.filters,
            "components": self.components
        }


def _from_key_value_pairs(pairs: [str]) -> dict[str, str]:
    """DOCSTRING"""

    if not pairs:
        return {}

    _pairs = {}

    for p in pairs:
        ndx = p.index("=")

        key = p[:ndx]
        value = p[ndx+1:]

        if not _KEY.match(key):
            raise v1.exceptions.RuntimeError(f"{key}: invalid key")

        _pairs[key] = value

    return _pairs


def _from_components(components: dict[str, dag.Component]) -> dict[str, object]:
    """DOCSTRING"""

    return {
        component.name: {
            "type": component.type,
            "parameters": component.parameters,
            "labels": [
                f"{name}={value}" for name, value in component.labels.items()
            ]
        } for component in components.values()
    }


def _from_links(links: dict[str, dag.Link]) -> dict[str, object]:
    """DOCSTRING"""

    return {
        link.name: {
            "type": link.type,
            "source": link.source,
            "destination": link.destination,
            "parameters": link.parameters,
            "labels": [
                f"{name}={value}" for name, value in link.labels.items()
            ]
        } for link in links.values()
    }


def _from_deployments(deployments: dict[str, Deployment]) -> dict[str, object]:
    """DOCSTRING"""

    return {
        "version": "torquetech.io/v1",
        "deployments": {
            deployment.name: {
                "context": {
                    "type": deployment.context_type,
                    "configuration": deployment.context_config
                },
                "strict": deployment.strict,
                "providers": deployment.providers or [],
                "extra_configuration": deployment.extra_configs or [],
                "filters": deployment.filters,
                "components": deployment.components
            } for deployment in deployments.values()
        }
    }


class Workspace:
    """DOCSTRING"""

    def __init__(self, workspace_path: str, deployments_path: str):
        self._workspace_path = workspace_path
        self._deployments_path = deployments_path

        self.repo = repository.load()

        self.dag = None
        self.deployments = None

        self._generate_dag()
        self._load_deployments()

    def _load_workspace_dag(self) -> dict[str, object]:
        """DOCSTRING"""

        if os.path.exists(self._workspace_path):
            with open(self._workspace_path, encoding="utf8") as file:
                workspace = yaml.safe_load(file)

        else:
            workspace = {
                "version": "torquetech.io/v1",
                "dag": {
                    "revision": 0,
                    "components": {},
                    "links": {}
                }
            }

        workspace = _WORKSPACE_SCHEMA.validate(workspace)

        if workspace["version"] != "torquetech.io/v1":
            raise v1.exceptions.RuntimeError(f"{workspace['version']}: invalid workspace version")

        return workspace["dag"]

    def _generate_dag(self) -> dag.DAG:
        """DOCSTRING"""

        workspace = self._load_workspace_dag()
        self.dag = dag.DAG(workspace["revision"])

        for name, component in workspace["components"].items():
            self.dag.create_component(name,
                                      component["type"],
                                      component["parameters"],
                                      _from_key_value_pairs(component["labels"]))

        for name, link in workspace["links"].items():
            self.dag.create_link(name,
                                 link["type"],
                                 link["source"],
                                 link["destination"],
                                 link["parameters"],
                                 _from_key_value_pairs(link["labels"]))

        self.dag.verify()

    def _load_deployments(self):
        """DOCSTRING"""

        self.deployments = {}

        if not self._deployments_path:
            return

        if not os.path.exists(self._deployments_path):
            return

        with open(self._deployments_path, encoding="utf8") as file:
            deployments = yaml.safe_load(file)

        deployments = _DEPLOYMENTS_SCHEMA.validate(deployments)

        if deployments["version"] != "torquetech.io/v1":
            raise v1.exceptions.RuntimeError(f"{deployments['version']}: invalid deployments version")

        self.deployments = {
            name: Deployment(name,
                             deployment["context"]["type"],
                             deployment["context"]["configuration"],
                             deployment["strict"],
                             deployment["providers"],
                             deployment["extra_configuration"],
                             deployment["filters"],
                             deployment["components"])
            for name, deployment in deployments["deployments"].items()
        }

    def _create_bond(self,
                     obj_type: type,
                     obj_name: str,
                     bond_path: [str],
                     interface: type,
                     required: bool) -> v1.bond.Bond:
        # pylint: disable=W0613

        """DOCSTRING"""

        return v1.component.DummyInterfaceImplementation()

    def _component(self, component: dag.Component):
        """DOCSTRING"""

        type = self.repo.component(component.type)

        bound_interfaces = interfaces.bind_to_component(type,
                                                        component.name,
                                                        self._create_bond)

        return type(component.name,
                    component.parameters,
                    None,
                    None,
                    bound_interfaces)

    def _link(self,
              link: dag.Link,
              source: v1.component.Component,
              destination: v1.component.Component) -> v1.link.Link:
        """DOCSTRING"""

        type = self.repo.link(link.type)

        bound_interfaces = interfaces.bind_to_link(type,
                                                   link.name,
                                                   source,
                                                   destination,
                                                   self._create_bond)

        return type(link.name,
                    link.parameters,
                    None,
                    None,
                    source.name,
                    destination.name,
                    bound_interfaces)

    def _get_full_component_name(self, name: str) -> str:
        """DOCSTRING"""

        trie = pytrie.StringTrie(self.dag.components.items())
        names = trie.keys(prefix=name)

        if not names:
            raise exceptions.ComponentNotFound(name)

        if len(names) != 1:
            if name in names:
                return name

            raise v1.exceptions.RuntimeError(f"{name}: ambigous component name")

        return names[0]

    def _get_full_link_name(self, name: str) -> str:
        """DOCSTRING"""

        trie = pytrie.StringTrie(self.dag.links.items())
        names = trie.keys(prefix=name)

        if not names:
            raise exceptions.LinkNotFound(name)

        if len(names) != 1:
            if name in names:
                return name

            raise v1.exceptions.RuntimeError(f"{name}: ambigous link name")

        return names[0]

    def _get_full_deployment_name(self, name: str) -> str:
        """DOCSTRING"""

        trie = pytrie.StringTrie(self.deployments.items())
        names = trie.keys(prefix=name)

        if not names:
            raise exceptions.DeploymentNotFound(name)

        if len(names) != 1:
            if name in names:
                return name

            raise v1.exceptions.RuntimeError(f"{name}: ambigous deployment name")

        return names[0]

    def _resolve_components(self, components: [str]) -> [str]:
        """DOCSTRING"""

        if not components:
            return None

        trie = pytrie.StringTrie(self.dag.components.items())
        _components = []

        for name in components:
            names = trie.keys(prefix=name)

            if not names:
                raise exceptions.ComponentNotFound(name)

            if len(names) != 1:
                if name not in names:
                    raise v1.exceptions.RuntimeError(f"{name}: ambigous component name")

                _components.append(name)

            else:
                _components.append(names[0])

        return _components

    def create_deployment(self,
                          name: str,
                          context_type: str,
                          providers: [str],
                          extra_configs: [str],
                          filters: [str],
                          components: [str],
                          strict: bool,
                          no_suffix: bool) -> Deployment:
        """DOCSTRING"""

        if not _NAME.match(name):
            raise exceptions.InvalidName(name)

        if len(name) > _MAX_DEPLOYMENT_NAME_LENGTH:
            raise v1.exceptions.RuntimeError(f"{name}: deployment name too long")

        if not no_suffix:
            name = f"{name}-{v1.utils.random_suffix(4)}"

        context = self.repo.context(context_type)

        if name in self.deployments:
            raise exceptions.DeploymentExists(name)

        try:
            context_config = context.on_configuration({})

        except v1.schema.SchemaError as exc:
            raise v1.exceptions.RuntimeError(f"component parameters: {name}: {exc}") from exc

        components = self._resolve_components(components)

        deployment = Deployment(name,
                                context_type,
                                context_config,
                                strict,
                                providers,
                                extra_configs,
                                filters,
                                components)

        self.deployments[name] = deployment
        return deployment

    def remove_deployment(self, name: str) -> Deployment:
        """DOCSTRING"""

        name = self._get_full_deployment_name(name)

        if name not in self.deployments:
            raise exceptions.DeploymentNotFound(name)

        return self.deployments.pop(name)

    def load_deployment(self,
                        name: str,
                        load_configs: bool = True) -> deployment.Deployment:
        """DOCSTRING"""

        name = self._get_full_deployment_name(name)

        if name not in self.deployments:
            raise exceptions.DeploymentNotFound(name)

        d = self.deployments[name]

        return deployment.load(d.name,
                               d.filters,
                               d.components,
                               d.context_type,
                               d.context_config,
                               d.providers,
                               d.extra_configs,
                               d.strict,
                               load_configs,
                               self.dag,
                               self.repo)

    def get_deployment(self, name: str) -> dag.Component:
        """DOCSTRING"""

        name = self._get_full_deployment_name(name)
        return self.deployments[name]

    def create_component(self,
                         name: str,
                         type: str,
                         parameters: [str],
                         labels: [str],
                         no_suffix: bool) -> dag.Component:
        # pylint: disable=W0622

        """DOCSTRING"""

        if not _NAME.match(name):
            raise exceptions.InvalidName(name)

        if len(name) > _MAX_COMPONENT_NAME_LENGTH:
            raise v1.exceptions.RuntimeError(f"{name}: component name too long")

        if not no_suffix:
            name = f"{name}-{v1.utils.random_suffix(4)}"

        parameters = _from_key_value_pairs(parameters)
        labels = _from_key_value_pairs(labels)

        component_type = self.repo.component(type)

        try:
            parameters = component_type.on_parameters(parameters)

        except v1.schema.SchemaError as exc:
            raise v1.exceptions.RuntimeError(f"component parameters: {name}: {exc}") from exc

        component = self.dag.create_component(name,
                                              type,
                                              parameters,
                                              labels)

        instance = self._component(component)
        instance.on_create()

        self.dag.revision += 1

        return component

    def remove_component(self, name: str) -> dag.Component:
        """DOCSTRING"""

        name = self._get_full_component_name(name)
        component = self.dag.remove_component(name)

        instance = self._component(component)
        instance.on_remove()

        self.dag.revision += 1

        return component

    def get_component(self, name: str) -> dag.Component:
        """DOCSTRING"""

        name = self._get_full_component_name(name)
        return self.dag.get_component(name)

    def create_link(self,
                    name: str,
                    type: str,
                    parameters: [str],
                    labels: [str],
                    source: str,
                    destination: str,
                    no_suffix: bool) -> dag.Link:
        # pylint: disable=W0622,R0913

        """DOCSTRING"""

        if not name:
            name = f"link-{v1.utils.random_suffix(4)}"

        else:
            if len(name) > _MAX_LINK_NAME_LENGTH:
                raise v1.exceptions.RuntimeError(f"{name}: link name too long")

            if not _NAME.match(name):
                raise exceptions.InvalidName(name)

            if not no_suffix:
                name = f"{name}-{v1.utils.random_suffix(4)}"

        parameters = _from_key_value_pairs(parameters)
        labels = _from_key_value_pairs(labels)

        link_type = self.repo.link(type)

        try:
            parameters = link_type.on_parameters(parameters)

        except v1.schema.SchemaError as exc:
            raise v1.exceptions.RuntimeError(f"link parameters: {name}: {exc}") from exc

        source = self._get_full_component_name(source)
        destination = self._get_full_component_name(destination)

        link = self.dag.create_link(name,
                                    type,
                                    source,
                                    destination,
                                    parameters,
                                    labels)

        self.dag.verify()

        source = self._component(self.dag.components[link.source])
        destination = self._component(self.dag.components[link.destination])

        instance = self._link(link, source, destination)
        instance.on_create()

        self.dag.revision += 1

        return link

    def remove_link(self, name: str) -> dag.Link:
        """DOCSTRING"""

        name = self._get_full_link_name(name)
        link = self.dag.remove_link(name)

        source = self._component(self.dag.components[link.source])
        destination = self._component(self.dag.components[link.destination])

        instance = self._link(link, source, destination)
        instance.on_remove()

        self.dag.revision += 1

        return link

    def get_link(self, name: str) -> dag.Component:
        """DOCSTRING"""

        name = self._get_full_link_name(name)
        return self.dag.get_link(name)

    def _store_workspace(self):
        """DOCSTRING"""

        workspace = {
            "version": "torquetech.io/v1",
            "dag": {
                "revision": self.dag.revision,
                "components": _from_components(self.dag.components),
                "links": _from_links(self.dag.links)
            }
        }

        with open(f"{self._workspace_path}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(workspace,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self._workspace_path}.tmp", self._workspace_path)

    def _store_deployments(self):
        """DOCSTRING"""

        if not self._deployments_path:
            return

        with open(f"{self._deployments_path}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(_from_deployments(self.deployments),
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self._deployments_path}.tmp", self._deployments_path)

    def store(self):
        """DOCSTRING"""

        self._store_workspace()
        self._store_deployments()


def load(workspace_path: str, deployments_path: str = None) -> Workspace:
    """DOCSTRING"""

    workspace_path = v1.utils.torque_path(workspace_path)
    workspace_path = v1.utils.resolve_path(workspace_path)

    if deployments_path:
        deployments_path = v1.utils.torque_path(deployments_path)
        deployments_path = v1.utils.resolve_path(deployments_path)

    return Workspace(workspace_path, deployments_path)
