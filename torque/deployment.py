# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import sys
import threading
import typing

import yaml

from torque import exceptions
from torque import interfaces
from torque import jobs
from torque import model
from torque import repository
from torque import v1


_CONFIGURATION_SCHEMA = v1.schema.Schema({
    "version": str,
    "providers": {
        v1.schema.Optional(str): {
            "labels": [str],
            "configuration": dict,
            "binds": {
                v1.schema.Optional(str): {
                    "configuration": dict
                }
            },
            "interfaces": {
                v1.schema.Optional(str): {
                    "bind": str
                }
            }
        }
    },
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): {
                "configuration": dict,
                "binds": {
                    v1.schema.Optional(str): {
                        "configuration": dict
                    }
                },
                "interfaces": {
                    v1.schema.Optional(str): {
                        "bind": str
                    }
                }
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "configuration": dict
            }
        }
    },
    "binds": {
        v1.schema.Optional(str): {
            "configuration": dict
        }
    },
    "interfaces": {
        v1.schema.Optional(str): {
            "bind": str
        }
    }
})


def _validate_type_config(name: str, type: object, config: dict[str, object]):
    """TODO"""

    try:
        return type.on_configuration(config or {})

    except v1.schema.SchemaError as exc:
        if issubclass(type, v1.component.Component):
            type = "component"

        elif issubclass(type, v1.link.Link):
            type = "link"

        elif issubclass(type, v1.provider.Bind):
            type = "bind"

        exc_str = str(exc)
        exc_str = " " + exc_str.replace("\n", "\n ")

        raise RuntimeError(f"{type} configuration: {name}: {exc_str}") from exc


def _validate_deployment_config(name: str, config: dict[str, object]) -> dict[str, object]:
    """TODO"""

    try:
        return _CONFIGURATION_SCHEMA.validate(config)

    except v1.schema.SchemaError as exc:
        exc_str = str(exc)
        exc_str = " " + exc_str.replace("\n", "\n ")

        raise RuntimeError(f"deployment: {name}:\n{exc_str}") from exc


class Configuration:
    """TODO"""

    def __init__(self, config: dict[str, object]):
        self._config = config

    def set_revision(self, revision: int):
        """TODO"""

        self._config["dag"]["revision"] = revision

    def revision(self) -> int:
        """TODO"""

        return self._config["dag"]["revision"]

    def providers(self) -> [str]:
        """TODO"""

        return self._config["providers"].keys()

    def binds(self) -> [str]:
        """TODO"""

        return self._config["binds"].keys()

    def interfaces(self) -> [str]:
        """TODO"""

        return self._config["interfaces"].keys()

    def provider(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._config["providers"][name]

    def bind(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._config["binds"][name]

    def interface(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._config["interfaces"][name]

    def component(self, name: str) -> dict[str, object]:
        """TODO"""

        dag_config = self._config["dag"]

        return dag_config["components"][name]

    def link(self, name: str) -> dict[str, object]:
        """TODO"""

        dag_config = self._config["dag"]

        return dag_config["links"][name]

    def get(self) -> dict[str, object]:
        """TODO"""

        return self._config


class Deployment:
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 context: v1.deployment.Context,
                 configuration: Configuration,
                 dag: model.DAG,
                 repo: repository.Repository):
        # pylint: disable=R0913

        self._context = context
        self._configuration = configuration
        self._dag = dag
        self._repo = repo

        self._components: dict[str, v1.component.Component] = {}
        self._links: dict[str, v1.link.Link] = {}
        self._providers: dict[str, v1.provider.Provider] = None

        self._interfaces = None
        self._binds = None

        self._lock = threading.Lock()

    def _setup_providers(self):
        """TODO"""

        self._interfaces = {
            name: self._configuration.interface(name)["bind"]
            for name in self._configuration.interfaces()
        }

        self._binds = {
            name: self._configuration.bind(name)
            for name in self._configuration.binds()
        }

        self._providers = {}

        for name in self._configuration.providers():
            provider_profile = self._configuration.provider(name)

            provider_config = provider_profile["configuration"]
            provider_labels = provider_profile["labels"]
            provider_type = self._repo.provider(name)

            bound_interfaces = interfaces.bind_to_provider(provider_type,
                                                           name,
                                                           provider_labels,
                                                           self._bind_to_provider)

            self._providers[name] = provider_type(provider_config,
                                                  bound_interfaces)

    def _component(self, name: str) -> v1.component.Component:
        """TODO"""

        if name in self._components:
            return self._components[name]

        component = self._dag.components[name]
        component_profile = self._configuration.component(name)

        component_config = component_profile["configuration"]
        component_type = self._repo.component(component.type)

        component_config = _validate_type_config(component.name,
                                                 component_type,
                                                 component_config)

        bound_interfaces = interfaces.bind_to_component(component_type,
                                                        component.name,
                                                        component.labels,
                                                        self._bind_to_component)

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
        link_profile = self._configuration.link(name)

        link_config = link_profile["configuration"]
        link_type = self._repo.link(link.type)

        link_config = _validate_type_config(link.name,
                                            link_type,
                                            link_config)

        source = self._component(link.source)
        destination = self._component(link.destination)

        bound_interfaces = interfaces.bind_to_link(link_type,
                                                   source,
                                                   destination,
                                                   self._bind_to_component)

        link = link_type(link.name,
                         link.parameters,
                         link_config,
                         bound_interfaces,
                         source.name,
                         destination.name)

        self._links[link.name] = link
        return link

    def _get_provider_bind(self,
                           interface: type,
                           required: bool,
                           provider_name: str) -> (str, dict[str, object]):
        """TODO"""

        interface_class = v1.utils.fqcn(interface)
        provider_profile = self._configuration.provider(provider_name)

        local_interfaces = provider_profile["interfaces"]
        local_binds = provider_profile["binds"]

        if interface_class in local_interfaces:
            bind_name = local_interfaces[interface_class]["bind"]

        else:
            if interface_class not in self._interfaces:
                if required:
                    raise RuntimeError(f"{interface_class}: interface not bound")

                return None, None

            bind_name = self._interfaces[interface_class]

        if bind_name not in self._binds:
            raise RuntimeError(f"{bind_name}: bind not configured")

        bind_config = self._binds[bind_name]["configuration"]

        if bind_name in local_binds:
            local_bind_config = local_binds[bind_name]["configuration"]
            bind_config = v1.utils.merge_dicts(bind_config, local_bind_config)

        return bind_name, bind_config

    def _bind_to_provider(self,
                          interface: type,
                          required: bool,
                          provider_name: str,
                          provider_labels: [str]) -> v1.provider.Bind:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        bind_name, bind_config = self._get_provider_bind(interface,
                                                         required,
                                                         provider_name)

        if not bind_name:
            return None

        bind_type = self._repo.bind(bind_name)

        if not issubclass(bind_type, interface):
            raise exceptions.InvalidBind(bind_name, v1.utils.fqcn(interface))

        bind_config = _validate_type_config(bind_name,
                                            bind_type,
                                            bind_config)

        bind_provider_name = self._repo.provider_for(bind_name)
        bind_provider = self._providers[bind_provider_name]

        bound_interfaces = interfaces.bind_to_provider(bind_type,
                                                       provider_name,
                                                       provider_labels,
                                                       self._bind_to_provider)

        return bind_type(bind_config,
                         bind_provider,
                         provider_labels,
                         bound_interfaces,
                         self._context)

    def _get_component_bind(self,
                            interface: type,
                            required: bool,
                            component_name: str) -> (str, dict[str, object]):
        """TODO"""

        interface_class = v1.utils.fqcn(interface)
        component_profile = self._configuration.component(component_name)

        local_interfaces = component_profile["interfaces"]
        local_binds = component_profile["binds"]

        if interface_class in local_interfaces:
            bind_name = local_interfaces[interface_class]["bind"]

        else:
            if interface_class not in self._interfaces:
                if required:
                    raise RuntimeError(f"{interface_class}: interface not bound")

                return None, None

            bind_name = self._interfaces[interface_class]

        if bind_name not in self._binds:
            raise RuntimeError(f"{bind_name}: bind not configured")

        bind_config = self._binds[bind_name]["configuration"]

        if bind_name in local_binds:
            local_bind_config = local_binds[bind_name]["configuration"]
            bind_config = v1.utils.merge_dicts(bind_config, local_bind_config)

        return bind_name, bind_config

    def _bind_to_component(self,
                           interface: type,
                           required: bool,
                           component_name: str,
                           component_labels: [str]) -> v1.provider.Bind:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        bind_name, bind_config = self._get_component_bind(interface,
                                                          required,
                                                          component_name)

        if not bind_name:
            return None

        bind_type = self._repo.bind(bind_name)

        if not issubclass(bind_type, interface):
            raise exceptions.InvalidBind(bind_name, v1.utils.fqcn(interface))

        bind_config = _validate_type_config(bind_name,
                                            bind_type,
                                            bind_config)

        bind_provider_name = self._repo.provider_for(bind_name)
        bind_provider = self._providers[bind_provider_name]

        bound_interfaces = interfaces.bind_to_component(bind_type,
                                                        component_name,
                                                        component_labels,
                                                        self._bind_to_component)

        return bind_type(bind_config,
                         bind_provider,
                         component_labels,
                         bound_interfaces,
                         self._context)

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

            instance.on_build(self._context)

        self._execute(workers, _on_build)

    def apply(self, workers: int, dry_run: bool):
        """TODO"""

        self._setup_providers()

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

            instance.on_apply(self._context)

        self._execute(workers, _on_apply)

        for provider in self._providers.values():
            provider.on_apply(self._context, dry_run)

    def delete(self, dry_run: bool):
        """TODO"""

        self._setup_providers()

        for provider in reversed(self._providers.values()):
            provider.on_delete(self._context, dry_run)

    def command(self, provider: str, argv: [str]):
        """TODO"""

        self._setup_providers()

        self._providers[provider].on_command(self._context, argv)

    def dot(self) -> str:
        """TODO"""

        return self._dag.dot(self._context.deployment_name)

    def update(self):
        """TODO"""

        self._configuration.set_revision(self._dag.revision)

        self._context.set_object("configuration",
                                 "torque-workspace",
                                 self._configuration.get())

    def store(self):
        """TODO"""

        self._context.store()


def _create_context(name: str,
                    type: str,
                    config: dict,
                    repo: repository.Repository) -> v1.deployment.Context:
    """TODO"""

    context_type = repo.context(type)

    context = context_type(name, config)
    context.load()

    return context


def _load_defaults(providers: [str],
                   dag: model.DAG,
                   repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    provider_binds = []

    for provider_name in providers:
        for bind_name, mapped_provider_name in repo.bind_maps().items():
            if provider_name == mapped_provider_name:
                provider_binds.append(bind_name)

    interfaces = {}
    binds = {}

    for interface_name, interface_class in repo.interfaces().items():
        bind = None

        for bind_name in provider_binds:
            if issubclass(repo.bind(bind_name), interface_class):
                if not bind:
                    bind = bind_name

                binds[bind_name] = {
                    "configuration": repo.bind(bind_name).on_configuration({})
                }

        if bind:
            interfaces[interface_name] = {
                "bind": bind
            }

    return {
        "version": "torquetech.io/v1",
        "providers": {
            name: {
                "labels": [],
                "configuration": repo.provider(name).on_configuration({}),
                "binds": {},
                "interfaces": {}
            } for name in providers
        },
        "binds": binds,
        "interfaces": interfaces,
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: {
                    "configuration": repo.component(component.type).on_configuration({}) or {},
                    "binds": {},
                    "interfaces": {}
                } for component in dag.components.values()
            },
            "links": {
                link.name: {
                    "configuration": repo.link(link.type).on_configuration({}) or {}
                } for link in dag.links.values()
            }
        }
    }


def _load_configuration(context: v1.deployment.Context,
                        providers: [str],
                        dag: model.DAG,
                        repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    config = context.get_object("configuration", "torque-workspace")
    defaults = _load_defaults(providers, dag, repo)

    if not config:
        return defaults

    return v1.utils.merge_dicts(defaults, config)


def load(name: str,
         components: [str],
         context_type: str,
         context_config: dict,
         providers: [str],
         extra_configs: [str],
         dag: model.DAG,
         repo: repository.Repository) -> Deployment:
    # pylint: disable=R0913

    """TODO"""

    context = _create_context(name, context_type, context_config, repo)
    config = _load_configuration(context, providers, dag, repo)

    for extra_config in extra_configs:
        extra_config = v1.utils.resolve_path(extra_config)

        with open(extra_config, "r", encoding="utf-8") as file:
            config = v1.utils.merge_dicts(config, yaml.safe_load(file))

    config = _validate_deployment_config(name, config)

    if config["version"] != "torquetech.io/v1":
        raise RuntimeError(f"{config['version']}: invalid configuration version")

    config = Configuration(config)

    if dag.revision != config.revision():
        print("WARNING: deployment out of date", file=sys.stderr)

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)

    return Deployment(context, config, dag, repo)
