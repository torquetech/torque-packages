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
            "configuration": dict,
            "bonds": {
                v1.schema.Optional(str): {
                    "configuration": dict
                }
            },
            "interfaces": {
                v1.schema.Optional(str): {
                    "bond": str
                }
            }
        }
    },
    "dag": {
        "revision": int,
        "components": {
            v1.schema.Optional(str): {
                "configuration": dict,
                "bonds": {
                    v1.schema.Optional(str): {
                        "configuration": dict
                    }
                },
                "interfaces": {
                    v1.schema.Optional(str): {
                        "bond": str
                    }
                }
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "configuration": dict,
                "bonds": {
                    v1.schema.Optional(str): {
                        "configuration": dict
                    }
                },
                "interfaces": {
                    v1.schema.Optional(str): {
                        "bond": str
                    }
                }
            }
        }
    },
    "bonds": {
        v1.schema.Optional(str): {
            "configuration": dict
        }
    },
    "interfaces": {
        v1.schema.Optional(str): {
            "bond": str
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

        elif issubclass(type, v1.bond.Bond):
            type = "bond"

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

    def bonds(self) -> [str]:
        """TODO"""

        return self._config["bonds"].keys()

    def interfaces(self) -> [str]:
        """TODO"""

        return self._config["interfaces"].keys()

    def provider(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._config["providers"][name]

    def bond(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._config["bonds"][name]

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
        self._bonds = None

        self._lock = threading.Lock()

    def _setup_providers(self):
        """TODO"""

        self._interfaces = {
            name: self._configuration.interface(name)["bond"]
            for name in self._configuration.interfaces()
        }

        self._bonds = {
            name: self._configuration.bond(name)
            for name in self._configuration.bonds()
        }

        self._providers = {}

        for name in self._configuration.providers():
            profile = self._configuration.provider(name)

            config = profile["configuration"]
            type = self._repo.provider(name)

            config = _validate_type_config(name, type, config)

            bonds = interfaces.bind_to_provider(type,
                                                name,
                                                self._bind_to_provider)

            self._providers[name] = type(config, self._context, bonds)

    def _component(self, name: str) -> v1.component.Component:
        """TODO"""

        if name in self._components:
            return self._components[name]

        component = self._dag.components[name]
        profile = self._configuration.component(name)

        config = profile["configuration"]
        type = self._repo.component(component.type)

        config = _validate_type_config(component.name, type, config)

        bonds = interfaces.bind_to_component(type,
                                             component.name,
                                             self._bind_to_component)

        component = type(component.name,
                         component.parameters,
                         config,
                         self._context,
                         bonds)

        self._components[component.name] = component

        return component

    def _link(self, name: str) -> v1.link.Link:
        """TODO"""

        if name in self._links:
            return self._links[name]

        link = self._dag.links[name]
        profile = self._configuration.link(name)

        config = profile["configuration"]
        type = self._repo.link(link.type)

        config = _validate_type_config(link.name, type, config)

        source = self._component(link.source)
        destination = self._component(link.destination)

        bonds = interfaces.bind_to_link(type,
                                        link.name,
                                        source,
                                        destination,
                                        self._bind_to_link)

        link = type(link.name,
                    link.parameters,
                    config,
                    self._context,
                    bonds,
                    source.name,
                    destination.name)

        self._links[link.name] = link

        return link

    def _get_bond_for(self,
                      interface: type,
                      required: bool,
                      profile: dict[str, object]) -> (str, dict[str, object]):
        """TODO"""

        interface_class = v1.utils.fqcn(interface)

        local_interfaces = profile["interfaces"]
        local_bonds = profile["bonds"]

        if interface_class in local_interfaces:
            name = local_interfaces[interface_class]["bond"]

        else:
            if interface_class not in self._interfaces:
                if required:
                    raise RuntimeError(f"{interface_class}: interface not bound")

                return None

            name = self._interfaces[interface_class]

        if name not in self._bonds:
            raise RuntimeError(f"{name}: bond not configured")

        config = self._bonds[name]["configuration"]

        if name in local_bonds:
            local_config = local_bonds[name]["configuration"]
            config = v1.utils.merge_dicts(config, local_config)

        return name, config

    def _bond_info(self,
                   interface: type,
                   required: bool,
                   profile: dict[str, object]) -> (v1.bond.Bond,
                                                   dict[str, object],
                                                   v1.provider.Provider):
        # pylint: disable=R0914

        """TODO"""

        info = self._get_bond_for(interface, required, profile)

        if not info:
            return None

        name, config = info

        type = self._repo.bond(name)

        if not issubclass(type, interface):
            raise exceptions.InvalidBond(name, v1.utils.fqcn(interface))

        config = _validate_type_config(name, type, config)

        provider_name = self._repo.provider_for(name)
        provider = self._providers[provider_name]

        return type, config, provider

    def _bind_to_provider(self,
                          interface: type,
                          required: bool,
                          provider_name: str) -> v1.bond.Bond:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        profile = self._configuration.provider(provider_name)
        info = self._bond_info(interface, required, profile)

        if not info:
            return None

        type, config, provider = info

        bonds = interfaces.bind_to_provider(type,
                                            provider_name,
                                            self._bind_to_provider)

        return type(provider,
                    config,
                    self._context,
                    bonds)

    def _bind_to_component(self,
                           interface: type,
                           required: bool,
                           component_name: str) -> v1.bond.Bond:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        profile = self._configuration.component(component_name)
        info = self._bond_info(interface, required, profile)

        if not info:
            return None

        type, config, provider = info

        bonds = interfaces.bind_to_component(type,
                                             component_name,
                                             self._bind_to_component)

        return type(provider,
                    config,
                    self._context,
                    bonds)

    def _bind_to_link(self,
                      interface: type,
                      required: bool,
                      link_name: str,
                      source: model.Component,
                      destination: model.Component) -> v1.bond.Bond:
        # pylint: disable=R0914

        """TODO"""

        if self._providers is None:
            return None

        profile = self._configuration.link(link_name)
        info = self._bond_info(interface, required, profile)

        if not info:
            return None

        type, config, provider = info

        bonds = interfaces.bind_to_link(type,
                                        link_name,
                                        source,
                                        destination,
                                        self._bind_to_link)

        return type(provider,
                    config,
                    self._context,
                    bonds)

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

            instance.on_build()

        self._execute(workers, _on_build)

    def apply(self, workers: int):
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

            instance.on_apply()

        self._execute(workers, _on_apply)

        for provider in self._providers.values():
            print(f"applying {v1.utils.fqcn(provider)}...")
            provider.apply()

    def delete(self):
        """TODO"""

        self._setup_providers()

        for provider in reversed(self._providers.values()):
            print(f"deleting {v1.utils.fqcn(provider)}...")
            provider.delete()

    def command(self, provider: str, argv: [str]):
        """TODO"""

        self._setup_providers()

        if provider not in self._providers:
            raise exceptions.ProviderNotFound(provider)

        self._providers[provider].command(argv)

    def dot(self) -> str:
        """TODO"""

        return self._dag.dot(self._context.deployment_name)

    def update(self):
        """TODO"""

        self._configuration.set_revision(self._dag.revision)

        with self._context as ctx:
            ctx.set_data("configuration", Deployment, self._configuration.get())

    def store(self):
        """TODO"""

        self._context.store()


def _create_context(name: str,
                    type: str,
                    config: dict,
                    repo: repository.Repository) -> v1.deployment.Context:
    """TODO"""

    context_type = repo.context(type)
    return context_type(name, config)


def _load_defaults(providers: [str],
                   dag: model.DAG,
                   repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    if len(set(providers)) != len(providers):
        raise RuntimeError("provider specified more than once")

    provider_bonds = []

    for provider_name in providers:
        for bond_name, mapped_provider_name in repo.bond_maps().items():
            if provider_name == mapped_provider_name:
                provider_bonds.append(bond_name)

    interfaces = {}
    bonds = {}

    for interface_name, interface_class in repo.interfaces().items():
        bond = None

        for bond_name in provider_bonds:
            if issubclass(repo.bond(bond_name), interface_class):
                if not bond:
                    bond = bond_name

                bonds[bond_name] = {
                    "configuration": repo.bond(bond_name).on_configuration({})
                }

        if bond:
            interfaces[interface_name] = {
                "bond": bond
            }

    return {
        "version": "torquetech.io/v1",
        "providers": {
            name: {
                "configuration": repo.provider(name).on_configuration({}),
                "bonds": {},
                "interfaces": {}
            } for name in providers
        },
        "bonds": bonds,
        "interfaces": interfaces,
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: {
                    "configuration": repo.component(component.type).on_configuration({}) or {},
                    "bonds": {},
                    "interfaces": {}
                } for component in dag.components.values()
            },
            "links": {
                link.name: {
                    "configuration": repo.link(link.type).on_configuration({}) or {},
                    "bonds": {},
                    "interfaces": {}
                } for link in dag.links.values()
            }
        }
    }


def _load_configuration(context: v1.deployment.Context,
                        providers: [str],
                        dag: model.DAG,
                        repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    with context as ctx:
        config = ctx.get_data("configuration", Deployment)

    defaults = _load_defaults(providers, dag, repo)

    if not config:
        return defaults

    return v1.utils.merge_dicts(defaults, config)


def load(name: str,
         components: [str],
         context_type: str,
         context_config: dict,
         strict: bool,
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
        if strict:
            raise RuntimeError(f"ERROR: {name}: deployment out of date")

        print(f"WARNING: {name}: deployment out of date", file=sys.stderr)

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)

    return Deployment(context, config, dag, repo)
