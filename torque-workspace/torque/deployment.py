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


CONFIGURATION_SCHEMA = v1.schema.Schema({
    "version": str,
    "interfaces": {
        v1.schema.Optional(str): {
            "default": str,
            "bonds": {
                v1.schema.Optional(str): {
                    "configuration": dict
                }
            }
        }
    },
    "providers": {
        v1.schema.Optional(str): {
            "configuration": dict,
            "bonds": {
                v1.schema.Optional(str): {
                    "implementation": v1.schema.Or(str, None),
                    "configuration": dict
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
                        "implementation": v1.schema.Or(str, None),
                        "configuration": dict
                    }
                }
            }
        },
        "links": {
            v1.schema.Optional(str): {
                "configuration": dict,
                "bonds": {
                    v1.schema.Optional(str): {
                        "implementation": v1.schema.Or(str, None),
                        "configuration": dict
                    }
                }
            }
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

        raise v1.exceptions.RuntimeError(f"{type} configuration: {name}:\n{exc_str}") from exc


def _validate_deployment_config(name: str, config: dict[str, object]) -> dict[str, object]:
    """TODO"""

    try:
        return CONFIGURATION_SCHEMA.validate(config)

    except v1.schema.SchemaError as exc:
        exc_str = str(exc)
        exc_str = " " + exc_str.replace("\n", "\n ")

        raise v1.exceptions.RuntimeError(f"deployment: {name}:\n{exc_str}") from exc


class _DummyInterfaceImplementation:
    """TODO"""

    def __getattribute__(self, attr):
        """TOOD"""

        return None


class _Configuration:
    """TODO"""

    def __init__(self, config: dict[str, object]):
        self._config = config

    def set_revision(self, revision: int):
        """TODO"""

        self._config["dag"]["revision"] = revision

    def revision(self) -> int:
        """TODO"""

        return self._config["dag"]["revision"]

    def interfaces(self) -> [str]:
        """TODO"""

        return self._config["interfaces"]

    def bonds(self, interface: str) -> [str]:
        """TODO"""

        return self._config["interfaces"][interface]["bonds"]

    def providers(self) -> [str]:
        """TODO"""

        return self._config["providers"].keys()

    def provider(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._config["providers"][name]

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
    """TODO"""

    def __init__(self,
                 context: v1.deployment.Context,
                 configuration: _Configuration,
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

        self._lock = threading.Lock()

    def _setup_providers(self):
        """TODO"""

        self._providers = {}

        for name in self._configuration.providers():
            profile = self._configuration.provider(name)
            config = profile["configuration"]

            type = self._repo.provider(name)

            config = _validate_type_config(name, type, config)

            bound_interfaces = interfaces.bind_to_provider(type,
                                                           self._create_bond,
                                                           self._bind_provider)

            self._providers[name] = type(config, self._context, bound_interfaces)

    def _bind_provider(self,
                       interface: type,
                       required: bool) -> v1.provider.Provider:
        """TODO"""

        if self._providers is None:
            return None

        name = v1.utils.fqcn(interface)
        provider = self._providers.get(name)

        if not provider:
            if required:
                raise exceptions.ProviderNotFound(name)

            return None

        return provider

    def _bond_info(self,
                   obj_name: str,
                   instance_name: str,
                   interface: type,
                   required: bool,
                   profile: dict[str, object]) -> (v1.bond.Bond, dict[str, object]):
        """TODO"""

        interfaces = self._configuration.interfaces()
        interface_name = v1.utils.fqcn(interface)

        if interface_name not in interfaces:
            if not required:
                return None

            raise exceptions.InterfaceNotFound(interface_name)

        bonds = self._configuration.bonds(interface_name)
        local_bonds = profile["bonds"]

        if instance_name in local_bonds:
            name = local_bonds[instance_name]["implementation"]
            config = local_bonds[instance_name]["configuration"]

            if name is None:
                if not required:
                    return None

                raise exceptions.InterfaceNotBound(f"{obj_name}-{instance_name}")

        else:
            name = interfaces[interface_name]["default"]
            config = {}

        if name not in bonds:
            if not required:
                return None

            raise exceptions.BondNotFound(name)

        type = self._repo.bond(name)

        if interface is not type.IMPLEMENTS:
            raise exceptions.InvalidBond(f"{obj_name}-{instance_name}", name)

        config = v1.utils.merge_dicts(bonds[name]["configuration"], config)
        config = _validate_type_config(f"{obj_name}-{instance_name}", type, config)

        return type, config

    def _create_bond(self,
                     obj_type: type,
                     obj_name: str,
                     bond_path: [str],
                     interface: type,
                     required: bool) -> v1.bond.Bond:
        """TODO"""

        if self._providers is None:
            return _DummyInterfaceImplementation()

        if issubclass(obj_type, v1.component.Component):
            profile = self._configuration.component(obj_name)

        elif issubclass(obj_type, v1.link.Link):
            profile = self._configuration.link(obj_name)

        elif issubclass(obj_type, v1.provider.Provider):
            profile = self._configuration.provider(obj_name)

        else:
            assert False

        instance_name = "-".join(bond_path)

        info = self._bond_info(obj_name, instance_name, interface, required, profile)

        if not info:
            return None

        type, config = info

        bound_interfaces = interfaces.bind_to_bond(obj_type,
                                                   obj_name,
                                                   bond_path,
                                                   type,
                                                   self._create_bond,
                                                   self._bind_provider)

        return type(f"{obj_name}-{instance_name}",
                    config,
                    self._context,
                    bound_interfaces)

    def _component(self, name: str) -> v1.component.Component:
        """TODO"""

        if name in self._components:
            return self._components[name]

        component = self._dag.components[name]
        profile = self._configuration.component(name)

        config = profile["configuration"]
        type = self._repo.component(component.type)

        config = _validate_type_config(component.name, type, config)

        bound_interfaces = interfaces.bind_to_component(type,
                                                        component.name,
                                                        self._create_bond)

        component = type(component.name,
                         component.parameters,
                         config,
                         self._context,
                         bound_interfaces)

        self._components[name] = component

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

        bound_interfaces = interfaces.bind_to_link(type,
                                                   link.name,
                                                   source,
                                                   destination,
                                                   self._create_bond)

        link = type(link.name,
                    link.parameters,
                    config,
                    self._context,
                    source.name,
                    destination.name,
                    bound_interfaces)

        self._links[name] = link

        return link

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

            print(f"building {name}...")

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

            print(f"applying {name}...")

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
            provider.run_hooks("apply-objects", op="applying", quiet=False)
            provider.run_hooks("apply-utils", op="applying", quiet=False)
            provider.run_hooks("apply", op="applying", quiet=False)

        for provider in reversed(self._providers.values()):
            provider.run_hooks("collect-garbage", reverse=True)

    def delete(self):
        """TODO"""

        self._setup_providers()

        for provider in reversed(self._providers.values()):
            provider.run_hooks("delete", op="deleting", quiet=False)

        for provider in reversed(self._providers.values()):
            provider.run_hooks("collect-garbage", reverse=True)

    def load_object(self, name: str) -> dict[str, object]:
        """TODO"""

        return self._context.load_bucket(name)

    def store_object(self, name: str, data: dict[str, object]):
        """TODO"""

        self._context.store_bucket(name, data)

    def update(self):
        """TODO"""

        self._configuration.set_revision(self._dag.revision)

        with self._context as ctx:
            ctx.set_data("configuration",
                         v1.utils.fqcn(Deployment),
                         self._configuration.get())

    def store(self):
        """TODO"""

        self._context.store()

    def dot(self) -> str:
        """TODO"""

        return self._dag.dot(self._context.deployment_name)


def _create_context(name: str,
                    type: str,
                    config: dict,
                    repo: repository.Repository) -> v1.deployment.Context:
    """TODO"""

    context_type = repo.context(type)
    return context_type(name, config)


def _bond_defaults(type: v1.bond.Bond) -> dict[str, object]:
    """TODO"""

    config = type.on_configuration({})

    return {
        "configuration": config
    }


def _provider_defaults(name: str,
                       repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    type = repo.provider(name)

    config = type.on_configuration({})

    return {
        "configuration": config,
        "bonds": {}
    }


def _component_defaults(component: model.Component,
                        repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    type = repo.component(component.type)
    config = type.on_configuration({})

    return {
        "configuration": config,
        "bonds": {}
    }


def _link_defaults(link: model.Link,
                   repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    type = repo.link(link.type)
    config = type.on_configuration({})

    return {
        "configuration": config,
        "bonds": {}
    }


def _load_defaults(providers: [str],
                   dag: model.DAG,
                   repo: repository.Repository) -> dict[str, object]:
    """TODO"""

    if len(set(providers)) != len(providers):
        raise v1.exceptions.RuntimeError("provider specified more than once")

    interfaces = {}
    provider_bonds = {}

    for bond_name, bond in repo.bonds().items():
        provider_name = v1.utils.fqcn(bond.PROVIDER)

        if provider_name not in provider_bonds:
            provider_bonds[provider_name] = []

        provider_bonds[provider_name].append((bond_name, bond))

    for provider in providers:
        if provider not in provider_bonds:
            continue

        for bond_name, bond in provider_bonds[provider]:
            interface = v1.utils.fqcn(bond.IMPLEMENTS)

            if interface not in interfaces:
                interfaces[interface] = {
                    "default": bond_name,
                    "bonds": {}
                }

            interfaces[interface]["bonds"].update({
                bond_name: _bond_defaults(bond)
            })

    return {
        "version": "torquetech.io/v1",
        "interfaces": interfaces,
        "providers": {
            name: _provider_defaults(name, repo)
            for name in providers
        },
        "dag": {
            "revision": dag.revision,
            "components": {
                component.name: _component_defaults(component, repo)
                for component in dag.components.values()
            },
            "links": {
                link.name: _link_defaults(link, repo)
                for link in dag.links.values()
            }
        }
    }


def _load_configuration(context: v1.deployment.Context,
                        providers: [str],
                        dag: model.DAG,
                        repo: repository.Repository,
                        strict: bool) -> dict[str, object]:
    """TODO"""

    with context as ctx:
        config = ctx.get_data("configuration", v1.utils.fqcn(Deployment))

    if not strict:
        defaults = _load_defaults(providers, dag, repo)

    else:
        defaults = {}

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
    config = _load_configuration(context, providers, dag, repo, strict)

    for extra_config in extra_configs:
        extra_config = v1.utils.resolve_path(extra_config)

        with open(extra_config, "r", encoding="utf-8") as file:
            config = v1.utils.merge_dicts(config, yaml.safe_load(file))

    config = _validate_deployment_config(name, config)

    if config["version"] != "torquetech.io/v1":
        raise v1.exceptions.RuntimeError(f"{config['version']}: invalid configuration version")

    config = _Configuration(config)

    if dag.revision != config.revision():
        if strict:
            raise v1.exceptions.RuntimeError(f"ERROR: {name}: deployment out of date")

        print(f"WARNING: {name}: deployment out of date", file=sys.stderr)

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)

    return Deployment(context, config, dag, repo)
