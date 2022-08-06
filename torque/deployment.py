# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import sys
import threading
import typing

from torque import exceptions
from torque import interfaces
from torque import jobs
from torque import model
from torque import profile
from torque import repository
from torque import v1


def _validate_config(name: str, type: object, config: dict):
    """TODO"""

    try:
        return type.on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        if isinstance(type, v1.component.Component):
            type = "component"

        elif isinstance(type, v1.link.Link):
            type = "link"

        elif isinstance(type, v1.provider.Interface):
            type = "bind"

        raise RuntimeError(f"{type} configuration: {name}: {exc}") from exc


class Deployment:
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 name: str,
                 profile: str,
                 dag: model.DAG,
                 interfaces: dict,
                 binds: dict,
                 repo: repository.Repository):
        # pylint: disable=R0913

        self._name = name
        self._profile = profile
        self._dag = dag
        self._interfaces = interfaces
        self._binds = binds
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

        for name in self._profile.providers():
            config = self._profile.provider(name)["configuration"]
            provider = self._repo.provider(name)(config)

            self._providers[name] = provider

    def _component(self, name: str) -> v1.component.Component:
        """TODO"""

        if name in self._components:
            return self._components[name]

        component = self._dag.components[name]
        component_config = self._profile.component(name)["configuration"]
        component_type = self._repo.component(component.type)

        component_config = _validate_config(component.name,
                                            component_type,
                                            component_config)

        bound_interfaces = interfaces.bind_to_component(component_type,
                                                        component.name,
                                                        component.labels,
                                                        self._bind_interface)

        component = component_type(component.name,
                                   component.labels,
                                   component.parameters,
                                   component_config,
                                   bound_interfaces)

        self._components[component.name] = component
        return component

    def _link(self, name: str) -> v1.link.Link:
        """TODO"""

        if name in self._links:
            return self._links[name]

        link = self._dag.links[name]
        link_config = self._profile.link(name)["configuration"]
        link_type = self._repo.link(link.type)

        link_config = _validate_config(link.name,
                                       link_type,
                                       link_config)

        source = self._component(link.source)
        destination = self._component(link.destination)

        bound_interfaces = interfaces.bind_to_link(link_type,
                                                   source,
                                                   destination,
                                                   self._bind_interface)

        link = link_type(link.name,
                         link.parameters,
                         link_config,
                         bound_interfaces,
                         source.name,
                         destination.name)

        self._links[link.name] = link
        return link

    def _bind_for(self, interface: type, required: bool, component_name: str) -> (str, dict):
        """TODO"""

        interface_class = v1.utils.fqcn(interface)

        local_interfaces = self._profile.component(component_name)["interfaces"]
        local_binds = self._profile.component(component_name)["binds"]

        if interface_class in local_interfaces:
            bind_name = local_interfaces[interface_class]["bind"]

        else:
            if interface_class not in self._interfaces:
                if required:
                    RuntimeError(f"{interface_class}: interface not bound")

                else:
                    return (None, None)

            bind_name = self._interfaces[interface_class]

        if bind_name not in self._binds:
            raise RuntimeError(f"{bind_name}: bind not configured")

        bind_config = self._binds[bind_name]["configuration"]

        if bind_name in local_binds:
            local_bind_config = local_binds[bind_name]["configuration"]
            bind_config = v1.utils.merge_dicts(bind_config, local_bind_config)

        return bind_name, bind_config


    def _bind_interface(self,
                        interface: type,
                        required: bool,
                        component_name: str,
                        component_labels: [str]) -> v1.provider.Interface:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        bind_name, bind_config = self._bind_for(interface, required, component_name)

        if not bind_name:
            return None

        bind_type = self._repo.bind(bind_name)

        if not issubclass(bind_type, interface):
            raise exceptions.InvalidBind(bind_name, interface_class)

        bind_config = _validate_config(bind_name,
                                       bind_type,
                                       bind_config)

        provider_name = self._repo.provider_for(bind_name)
        provider = self._providers[provider_name]

        bound_interfaces = interfaces.bind_to_component(bind_type,
                                                        component_name,
                                                        component_labels,
                                                        self._bind_interface)

        return bind_type(bind_config,
                         provider,
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

    interfaces = {
        name: profile.interface(name)["bind"] for name in profile.interfaces()
    }

    binds = {
        name: profile.bind(name) for name in profile.binds()
    }

    dag = dag.subset(components)

    return Deployment(name, profile, dag, interfaces, binds, repo)
