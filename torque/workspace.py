# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import re
import secrets
import sys

import yaml

from torque import deployment
from torque import exceptions
from torque import interfaces
from torque import model
from torque import repository
from torque import v1


_PROTO = r"^([^:]+)://"
_NAME = r"^[A-Za-z_][A-Za-z0-9_]*$"

_WORKSPACE_SCHEMA = v1.schema.Schema({
    "version": str,
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): {
                "type": str,
                "labels": [str],
                "parameters": dict
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "type": str,
                "source": str,
                "destination": str,
                "parameters": dict
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
            "providers": [str],
            "extra_configuration": [str],
            "labels": v1.schema.Or([str], None),
            "components": v1.schema.Or([str], None)
        }
    }
})


class Deployment:
    """TODO"""

    def __init__(self,
                 name: str,
                 context_type: str,
                 context_config: dict[str, object],
                 providers: str,
                 extra_configs: [str],
                 labels: [str],
                 components: [str]):
        self.name = name
        self.context_type = context_type
        self.context_config = context_config
        self.providers = providers
        self.extra_configs = extra_configs
        self.labels = labels
        self.components = components

    def __repr__(self) -> str:
        return \
            f"Deployment({self.name}" \
            f", context_type={self.context_type}" \
            f", providers={self.providers}" \
            f", labels={self.labels} " \
            f", components={self.components})"


def _from_components(components: dict[str, model.Component]) -> dict[str, object]:
    """TODO"""

    return {
        component.name: {
            "type": component.type,
            "labels": component.labels,
            "parameters": component.parameters
        } for component in components.values()
    }


def _from_links(links: dict[str, model.Link]) -> dict[str, object]:
    """TODO"""

    return {
        link.name: {
            "type": link.type,
            "source": link.source,
            "destination": link.destination,
            "parameters": link.parameters
        } for link in links.values()
    }


def _from_deployments(deployments: dict[str, Deployment]) -> dict[str, object]:
    """TODO"""

    return {
        "version": "torquetech.io/v1",
        "deployments": {
            deployment.name: {
                "context": {
                    "type": deployment.context_type,
                    "configuration": deployment.context_config
                },
                "providers": deployment.providers,
                "extra_configuration": deployment.extra_configs or [],
                "labels": deployment.labels,
                "components": deployment.components
            } for deployment in deployments.values()
        }
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
                 workspace_path: str,
                 deployments_path: str,
                 deployments: dict[str, Deployment],
                 dag: model.DAG,
                 repo: repository.Repository):
        # pylint: disable=R0913

        self.dag = dag
        self.repo = repo
        self.deployments = deployments

        self._workspace_path = workspace_path
        self._deployments_path = deployments_path

    def _bind_interface(self,
                        interface: object,
                        required: bool,
                        component_name: str,
                        component_labels: [str]) -> v1.provider.Bind:
        # pylint: disable=W0613

        """TODO"""

        return None

    def _component(self, component: model.Component):
        """TODO"""

        type = self.repo.component(component.type)
        bound_interfaces = interfaces.bind_to_component(type,
                                                        component.name,
                                                        component.labels,
                                                        self._bind_interface)

        return type(component.name,
                    component.labels,
                    component.parameters,
                    None,
                    bound_interfaces)

    def _link(self,
              link: model.Link,
              source: v1.component.Component,
              destination: v1.component.Component) -> v1.link.Link:
        """TODO"""

        type = self.repo.link(link.type)
        bound_interfaces = interfaces.bind_to_link(type,
                                                   source,
                                                   destination,
                                                   self._bind_interface)

        return type(link.name,
                    link.parameters,
                    None,
                    bound_interfaces,
                    source.name,
                    destination.name)

    def _collect_components_for(self, name: str) -> [str]:
        """TODO"""

        deployment = self.deployments[name]

        labels = deployment.labels
        components = deployment.components

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

    def _process_names(self, names: list) -> dict[str, [str]]:
        """TODO"""

        names = [n.split(".") for n in names]
        processed = {}

        for n, r in names:
            if n in processed:
                processed[n].append(r)

            else:
                processed[n] = [r]

        return processed

    def _get_full_component_name(self, name: str) -> str:
        """TODO"""

        if '.' in name:
            return name

        processed = self._process_names(self.dag.components.keys())

        if name not in processed:
            raise exceptions.ComponentNotFound(name)

        if len(processed[name]) != 1:
            raise RuntimeError(f"{name}: ambigous component name")

        return f"{name}.{processed[name][0]}"

    def _get_full_link_name(self, name: str) -> str:
        """TODO"""

        if '.' in name:
            return name

        processed = self._process_names(self.dag.links.keys())

        if name not in processed:
            raise exceptions.LinkNotFound(name)

        if len(processed[name]) != 1:
            raise RuntimeError(f"{name}: ambigous link name")

        return f"{name}.{processed[name][0]}"

    def _get_full_deployment_name(self, name: str) -> str:
        """TODO"""

        if '.' in name:
            return name

        processed = self._process_names(self.deployments.keys())

        if name not in processed:
            raise exceptions.DeploymentNotFound(name)

        if len(processed[name]) != 1:
            raise RuntimeError(f"{name}: ambigous deployment name")

        return f"{name}.{processed[name][0]}"

    def create_deployment(self,
                          name: str,
                          context_type: str,
                          providers: [str],
                          extra_configs: [str],
                          labels: [str],
                          components: [str]) -> Deployment:
        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        name = f"{name}.{secrets.token_hex(2)[:3]}"
        context = self.repo.context(context_type)

        if name in self.deployments:
            raise exceptions.DeploymentExists(name)

        try:
            context_config = context.on_configuration({})

        except v1.schema.SchemaError as exc:
            raise RuntimeError(f"component parameters: {name}: {exc}") from exc

        for component in components or []:
            if component not in self.dag.components:
                raise exceptions.ComponentNotFound(component)

        deployment = Deployment(name,
                                context_type,
                                context_config,
                                providers,
                                extra_configs,
                                labels,
                                components)

        self.deployments[name] = deployment
        return deployment

    def remove_deployment(self, name: str) -> Deployment:
        """TODO"""

        name = self._get_full_deployment_name(name)

        if name not in self.deployments:
            raise exceptions.DeploymentNotFound(name)

        return self.deployments.pop(name)

    def load_deployment(self,
                        name: str,
                        load_extra_configs: bool = True) -> deployment.Deployment:
        """TODO"""

        name = self._get_full_deployment_name(name)

        if name not in self.deployments:
            raise exceptions.DeploymentNotFound(name)

        components = self._collect_components_for(name)
        d = self.deployments[name]

        return deployment.load(d.name,
                               components,
                               d.context_type,
                               d.context_config,
                               d.providers,
                               d.extra_configs if load_extra_configs else [],
                               self.dag,
                               self.repo)

    def create_component(self,
                         name: str,
                         type: str,
                         labels: [str],
                         params: object) -> model.Component:
        # pylint: disable=W0622

        """TODO"""

        if not re.match(_NAME, name):
            raise exceptions.InvalidName(name)

        name = f"{name}.{secrets.token_hex(2)[:3]}"
        component_type = self.repo.component(type)

        try:
            params = component_type.on_parameters(params)

        except v1.schema.SchemaError as exc:
            raise RuntimeError(f"component parameters: {name}: {exc}") from exc

        component = self.dag.create_component(name, type, labels, params)

        instance = self._component(component)
        instance.on_create()

        self.dag.revision += 1

        return component

    def remove_component(self, name: str) -> model.Component:
        """TODO"""

        name = self._get_full_component_name(name)
        component = self.dag.remove_component(name)

        instance = self._component(component)
        instance.on_remove()

        self.dag.revision += 1

        return component

    def get_component(self, name: str) -> model.Component:
        """TODO"""

        name = self._get_full_component_name(name)
        return self.dag.get_component(name)

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

        name = f"{name}.{secrets.token_hex(2)[:3]}"
        link_type = self.repo.link(type)

        try:
            params = link_type.on_parameters(params)

        except v1.schema.SchemaError as exc:
            raise RuntimeError(f"link parameters: {name}: {exc}") from exc

        source = self._get_full_component_name(source)
        destination = self._get_full_component_name(destination)

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

        name = self._get_full_link_name(name)
        link = self.dag.remove_link(name)

        source = self._component(self.dag.components[link.source])
        destination = self._component(self.dag.components[link.destination])

        instance = self._link(link, source, destination)
        instance.on_remove()

        self.dag.revision += 1

        return link

    def get_link(self, name: str) -> model.Component:
        """TODO"""

        name = self._get_full_link_name(name)
        return self.dag.get_link(name)

    def _store_workspace(self):
        """TODO"""

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
        """TODO"""

        if not self._deployments_path:
            return

        with open(f"{self._deployments_path}.tmp", "w", encoding="utf8") as file:
            yaml.safe_dump(_from_deployments(self.deployments),
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        os.replace(f"{self._deployments_path}.tmp", self._deployments_path)

    def store(self):
        """TODO"""

        self._store_workspace()
        self._store_deployments()


def _load_deployments(path: str) -> dict[str, Deployment]:
    """TODO"""

    if not path:
        return {}

    path = v1.utils.resolve_path(path)

    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf8") as file:
        deployments = yaml.safe_load(file)

    deployments = _DEPLOYMENTS_SCHEMA.validate(deployments)

    if deployments["version"] != "torquetech.io/v1":
        raise RuntimeError(f"{deployments['version']}: invalid deployments version")

    return {
        name: Deployment(name,
                         deployment["context"]["type"],
                         deployment["context"]["configuration"],
                         deployment["providers"],
                         deployment["extra_configuration"],
                         deployment["labels"],
                         deployment["components"])
        for name, deployment in deployments["deployments"].items()
    }


def load(workspace_path: str, deployments_path: str = None) -> Workspace:
    """TODO"""

    workspace_path = v1.utils.torque_path(workspace_path)
    workspace_path = v1.utils.resolve_path(workspace_path)

    if deployments_path:
        deployments_path = v1.utils.torque_path(deployments_path)
        deployments_path = v1.utils.resolve_path(deployments_path)

    if os.path.exists(workspace_path):
        with open(workspace_path, encoding="utf8") as file:
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
        raise RuntimeError(f"{workspace['version']}: invalid workspace version")

    deployments = _load_deployments(deployments_path)
    repo = repository.load()
    dag = _generate_dag(workspace)

    return Workspace(workspace_path, deployments_path, deployments, dag, repo)


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
