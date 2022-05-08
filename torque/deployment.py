# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import sys
import threading

from collections import namedtuple

from torque import exceptions
from torque import interfaces
from torque import jobs
from torque import model
from torque import profile
from torque import repository
from torque import v1


Configuration = namedtuple("Configuration", [
    "providers",
    "interfaces",
    "components",
    "links"
])


class Deployment:
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 name: str,
                 profile: str,
                 dag: model.DAG,
                 config: Configuration,
                 repo: repository.Repository):
        # pylint: disable=R0913

        self._name = name
        self._profile = profile
        self._dag = dag
        self._config = config
        self._repo = repo

        self._components: dict[str, v1.component.Component] = {}
        self._links: dict[str, v1.link.Link] = {}

        self._providers: dict[str, v1.provider.Provider] = None
        self._interfaces: dict[str, v1.provider.Interface] = None

        self._lock = threading.Lock()

    def _create_path(self) -> str:
        """TODO"""

        deployment_path = f"{v1.utils.torque_dir()}/local/deployments/{self._name}"

        if not os.path.exists(deployment_path):
            os.makedirs(deployment_path)

        return deployment_path

    def _setup_providers(self):
        """TODO"""

        self._providers = {}

        for name, config in self._config.providers.items():
            provider = self._repo.provider(name)(config)
            self._providers[name] = provider

    def _setup_interfaces(self):
        """TODO"""

        self._interfaces = {}

        for name in self._config.interfaces.keys():
            if name.startswith("::"):
                continue

            interface = self._repo.interface(name)

            if not issubclass(interface, v1.provider.Interface):
                raise RuntimeError(f"{v1.utils.fqcn(interface)}: invalid provider interface")

            cls = interface

            while cls is not v1.provider.Interface:
                if len(cls.__bases__) != 1:
                    raise RuntimeError(f"{v1.utils.fqcn(interface)}: multiple inheritance not supported")

                fqcn = v1.utils.fqcn(cls)

                if fqcn in self._interfaces:
                    print(f"WARNING: {name}: duplicate provider interface: {fqcn}")

                self._interfaces[fqcn] = name
                cls = cls.__bases__[0]

    def _component(self, name: str) -> v1.component.Component:
        """TODO"""

        if name in self._components:
            return self._components[name]

        config = self._config.components[name]
        component = self._dag.components[name]

        type = self._repo.component(component.type)
        bound_interfaces = interfaces.bind_to_component(type,
                                                        component.name,
                                                        component.labels,
                                                        self._interface)

        component = type(component.name,
                         component.labels,
                         component.parameters,
                         config,
                         bound_interfaces)

        self._components[component.name] = component
        return component

    def _link(self, name: str) -> v1.link.Link:
        """TODO"""

        if name in self._links:
            return self._links[name]

        config = self._config.links[name]
        link = self._dag.links[name]

        source = self._component(link.source)
        destination = self._component(link.destination)

        type = self._repo.link(link.type)
        bound_interfaces = interfaces.bind_to_link(type,
                                                   source,
                                                   destination,
                                                   self._interface)

        link = type(link.name,
                    link.parameters,
                    config,
                    bound_interfaces,
                    source.name,
                    destination.name)

        self._links[link.name] = link
        return link

    def _interface(self,
                   interface: type,
                   required: bool,
                   name: str,
                   labels: [str]) -> v1.provider.Interface:
        """TODO"""

        if self._interfaces is None:
            return None

        interface_class = v1.utils.fqcn(interface)

        if interface_class not in self._interfaces:
            if required:
                raise RuntimeError(f"{interface_class}: interface not found")

            return None

        interface_name = self._interfaces[interface_class]
        interface_type = self._repo.interface(interface_name)

        provider_name = self._repo.provider_for(interface_name)
        compound_name = f"::{name}::{interface_name}"

        if compound_name in self._config.interfaces:
            config = self._config.interfaces[compound_name]

        else:
            config = self._config.interfaces[interface_name]

        provider = self._providers[provider_name]

        bound_interfaces = interfaces.bind_to_component(interface_type,
                                                        interface_name,
                                                        labels,
                                                        self._interface)

        return interface_type(config, provider, name, labels, bound_interfaces)

    def _execute(self, workers: int, callback: callable):
        """TODO"""

        def _callback_helper(name: str) -> bool:
            type = name[:name.index("/")]
            name = name[len(type) + 1:]

            return callback(type, name)

        _jobs = []

        for component in self._dag.components.values():
            depends = []

            for inbound_links in component.inbound_links.values():
                depends += [f"link/{link}" for link in inbound_links]

            job = jobs.Job(f"component/{component.name}", depends, _callback_helper)
            _jobs.append(job)

            for outbound_links in component.outbound_links.values():
                for link in outbound_links:
                    depends = [f"component/{component.name}"]
                    job = jobs.Job(f"link/{link}", depends, _callback_helper)
                    _jobs.append(job)

        jobs.execute(workers, _jobs)

    def build(self, workers: int):
        """TODO"""

        path = self._create_path()
        deployment = v1.deployment.Deployment(self._name,
                                              self._profile,
                                              False,
                                              path)

        def _on_build(type: str, name: str):
            """TODO"""

            print(f"building {name}...", file=sys.stderr)

            with self._lock:
                if type == "component":
                    instance = self._component(name)

                elif type == "link":
                    instance = self._link(name)

                else:
                    assert False

            instance.on_build(deployment)

        self._execute(workers, _on_build)

    def apply(self, workers: int, dry_run: bool):
        """TODO"""

        self._setup_providers()
        self._setup_interfaces()

        path = self._create_path()
        deployment = v1.deployment.Deployment(self._name,
                                              self._profile,
                                              dry_run,
                                              path)

        def _on_apply(type: str, name: str):
            """TODO"""

            print(f"applying {name}...", file=sys.stderr)

            with self._lock:
                if type == "component":
                    instance = self._component(name)

                elif type == "link":
                    instance = self._link(name)

                else:
                    assert False

            instance.on_apply(deployment)

        self._execute(workers, _on_apply)

        for provider in self._providers.values():
            provider.on_apply(deployment)

    def delete(self, dry_run: bool):
        """TODO"""

        self._setup_providers()

        path = self._create_path()
        deployment = v1.deployment.Deployment(self._name,
                                              self._profile,
                                              dry_run,
                                              path)

        for provider in self._providers.values():
            provider.on_delete(deployment)

    def dot(self) -> str:
        """TODO"""

        return self._dag.dot(self._name)


def _provider_config(provider: str,
                     profile: profile.Profile,
                     repo: repository.Repository) -> dict:
    """TODO"""

    config = profile.provider(provider)

    try:
        return repo.provider(provider).on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"provider configuration: {provider}: {exc}") from exc


def _interface_config(interface: str,
                      profile: profile.Profile,
                      repo: repository.Repository) -> dict:
    """TODO"""

    config = profile.interface(interface)

    try:
        return repo.interface(interface).on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"interface configuration: {interface}: {exc}") from exc


def _component_interfaces(component: model.Component,
                          profile: profile.Profile,
                          repo: repository.Repository) -> dict:
    """TODO"""

    interfaces = {}

    for name, config in profile.component_interfaces(component.name).items():
        try:
            config = repo.interface(name).on_configuration(config or {})

        except v1.schema.SchemaError as exc:
            raise RuntimeError(f"interface configuration: {component.name}::{name}: {exc}") from exc

        name = f"::{component.name}::{name}"
        interfaces[name] = config

    return interfaces


def _component_config(component: model.Component,
                      profile: profile.Profile,
                      repo: repository.Repository) -> dict:
    """TODO"""
    config = profile.component(component.name)

    try:
        return repo.component(component.type).on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"component configuration: {component.name}: {exc}") from exc


def _link_config(link: model.Link,
                 profile: profile.Profile,
                 repo: repository.Repository) -> dict:
    """TODO"""
    config = profile.link(link.name)

    try:
        return repo.link(link.type).on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"link configuration: {link.name}: {exc}") from exc


def load(name: str,
         components: [str],
         profile: profile.Profile,
         dag: model.DAG,
         repo: repository.Repository) -> Deployment:
    # pylint: disable=R0913

    """TODO"""

    if dag.revision != profile.revision():
        print("WARNING: profile out of date", file=sys.stderr)

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)

    providers = {
        provider: _provider_config(provider, profile, repo)
        for provider in profile.providers()
    }

    interfaces = {
        interface: _interface_config(interface, profile, repo)
        for interface in profile.interfaces()
    }

    for component in dag.components.values():
        interfaces = interfaces | _component_interfaces(component, profile, repo)

    components = {
        component.name: _component_config(component, profile, repo)
        for component in dag.components.values()
    }

    links = {
        link.name: _link_config(link, profile, repo)
        for link in dag.links.values()
    }

    config = Configuration(providers, interfaces, components, links)

    return Deployment(name, profile.name, dag, config, repo)
