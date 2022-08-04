# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import sys
import threading
import typing

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
    "components",
    "links",
    "interfaces",
    "binds",
    "overrides"
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
                                                        self._bind_interface)

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
                                                   self._bind_interface)

        link = type(link.name,
                    link.parameters,
                    config,
                    bound_interfaces,
                    source.name,
                    destination.name)

        self._links[link.name] = link
        return link

    def _bind_interface(self,
                        interface: type,
                        required: bool,
                        component_name: str,
                        component_labels: [str]) -> v1.provider.Interface:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        interface_class = v1.utils.fqcn(interface)
        override_name = f"{component_name}::{interface_class}"

        if override_name in self._config.overrides:
            bind_name = self._config.overrides[override_name]

        else:
            interface_binds = self._config.interfaces[interface_class]
            binds = interface_binds["binds"]

            if not binds:
                if required:
                    RuntimeError(f"{interface_class}: interface not bound")

                else:
                    return None

            if len(binds) == 1:
                bind_name = binds[0]

            else:
                if "default" not in interface_binds:
                    bind_name = binds[0]

                    print(f"WARNING: {component_name}: {interface_class}: multiple binds found" "\n"
                          f"WARNING: default bind not specified, using {bind_name}")

                else:
                    bind_name = interface_binds["default"]

        bind_type = self._repo.bind(bind_name)

        if not issubclass(bind_type, interface):
            raise exceptions.InvalidBind(bind_name, interface_class)

        provider_name = self._repo.provider_for(bind_name)
        compound_name = f"{component_name}::{bind_name}"

        if compound_name in self._config.binds:
            config = self._config.binds[compound_name]

        else:
            if bind_name in self._config.binds:
                config = self._config.binds[bind_name]

            else:
                config = self._repo.bind(bind_name).on_configuration({})

        provider = self._providers[provider_name]

        bound_interfaces = interfaces.bind_to_component(bind_type,
                                                        component_name,
                                                        component_labels,
                                                        self._bind_interface)

        return bind_type(config,
                         provider,
                         component_name,
                         component_labels,
                         bound_interfaces)

    def _execute(self, workers: int, callback: typing.Callable):
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

        for provider in reversed(self._providers.values()):
            provider.on_delete(deployment)

    def dot(self) -> str:
        """TODO"""

        return self._dag.dot(self._name)


def _provider_config(name: str,
                     profile: profile.Profile,
                     repo: repository.Repository) -> dict:
    """TODO"""

    config = profile.provider(name)

    try:
        return repo.provider(name).on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"provider configuration: {name}: {exc}") from exc


def _bind_config(name: str,
                 profile: profile.Profile,
                 repo: repository.Repository) -> dict:
    """TODO"""

    config = profile.bind(name)

    try:
        return repo.bind(name).on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        raise RuntimeError(f"bind configuration: {name}: {exc}") from exc


def _component_binds_configs(component: model.Component,
                             profile: profile.Profile,
                             repo: repository.Repository) -> dict:
    """TODO"""

    binds = {}

    for name, bind in profile.component_binds(component.name).items():
        config = bind["configuration"]

        try:
            config = repo.bind(name).on_configuration(config or {})

        except v1.schema.SchemaError as exc:
            raise RuntimeError(f"bind configuration: {component.name}::{name}: {exc}") from exc

        name = f"{component.name}::{name}"
        binds[name] = config

    return binds


def _component_binds_overrides(component: model.Component,
                               profile: profile.Profile,
                               repo: repository.Repository) -> dict:
    # pylint: disable=W0613

    """TODO"""

    bind_overrides = {}

    for name, interface in profile.component_interfaces(component.name).items():
        name = f"{component.name}::{name}"
        bind_overrides[name] = interface["bind"]

    return bind_overrides


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


def _load_all_interfaces(providers: dict, repo: repository.Repository) -> dict:
    """TODO"""

    binds = []

    for provider_name in providers.keys():
        for bind_name, mapped_provider_name in repo.bind_maps().items():
            if provider_name == mapped_provider_name:
                binds.append(bind_name)

    interfaces = {}

    for interface_name, interface_class in repo.interfaces().items():
        interfaces[interface_name] = {}
        interface_binds = []

        for bind_name in binds:
            if issubclass(repo.bind(bind_name), interface_class):
                interface_binds.append(bind_name)

        interfaces[interface_name]["binds"] = interface_binds

    return interfaces


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

    components = {
        component.name: _component_config(component, profile, repo)
        for component in dag.components.values()
    }

    links = {
        link.name: _link_config(link, profile, repo)
        for link in dag.links.values()
    }

    binds = {
        bind: _bind_config(bind, profile, repo)
        for bind in profile.binds()
    }

    overrides = {}

    for component in dag.components.values():
        binds = v1.utils.merge_dicts(binds,  _component_binds_configs(component, profile, repo))
        overrides = v1.utils.merge_dicts(overrides, _component_binds_overrides(component, profile, repo))

    interfaces = _load_all_interfaces(providers, repo)
    interfaces = v1.utils.merge_dicts(interfaces, profile.interfaces())

    config = Configuration(providers,
                           components,
                           links,
                           interfaces,
                           binds,
                           overrides)

    return Deployment(name, profile.name, dag, config, repo)
