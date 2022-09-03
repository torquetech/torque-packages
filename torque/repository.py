# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import importlib
import traceback
import sys

from torque import defaults
from torque import exceptions
from torque import v1


def _is_component(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.component.Component)


def _is_link(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.link.Link)


def _is_provider(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.provider.Provider)


def _is_bond(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.bond.Bond)


def _is_context(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.deployment.Context)


_REPOSITORY_SCHEMA = v1.schema.Schema({
    v1.schema.Optional("v1"): v1.schema.Schema({
        v1.schema.Optional("contexts"): {
            v1.schema.Optional(str): _is_context
        },
        v1.schema.Optional("components"): {
            v1.schema.Optional(str): _is_component
        },
        v1.schema.Optional("links"): {
            v1.schema.Optional(str): _is_link
        },
        v1.schema.Optional("providers"): {
            v1.schema.Optional(str): _is_provider
        },
        v1.schema.Optional("interfaces"): [
            _is_bond
        ],
        v1.schema.Optional("bonds"): {
            v1.schema.Optional(str): [
                _is_bond
            ]
        }
    })
}, ignore_extra_keys=True)

_DEFAULT_REPOSITORY = {
    "v1": {
        "contexts": {
            "torquetech.io/local": defaults.LocalContext
        },
        "components": {
        },
        "links": {
            "torquetech.io/dependency": defaults.DependencyLink
        },
        "providers": {
        },
        "bonds": {
        }
    }
}


class Repository:
    """TODO"""

    def __init__(self, repo: dict[str, object]):
        self._repo = repo

        self._process_providers()

    def _process_providers(self):
        """TODO"""

        providers = {}
        bonds = {}
        bond_maps = {}

        for provider_name, provider_class in self._repo["v1"]["providers"].items():
            providers[provider_name] = provider_class

        for provider_name, provider_bonds in self._repo["v1"]["bonds"].items():
            for bond_name, bond_class in provider_bonds.items():
                bonds[bond_name] = bond_class
                bond_maps[bond_name] = provider_name

        self._repo["v1"]["providers"] = providers
        self._repo["v1"]["bonds"] = bonds
        self._repo["v1"]["bond_maps"] = bond_maps

    def contexts(self) -> dict[str, object]:
        """TODO"""

        return self._repo["v1"]["contexts"]

    def components(self) -> dict[str, object]:
        """TODO"""

        return self._repo["v1"]["components"]

    def links(self) -> dict[str, object]:
        """TODO"""

        return self._repo["v1"]["links"]

    def providers(self) -> dict[str, object]:
        """TODO"""

        return self._repo["v1"]["providers"]

    def interfaces(self) -> dict[str, object]:
        """TODO"""

        return self._repo["v1"]["interfaces"]

    def bonds(self) -> dict[str, object]:
        """TODO"""

        return self._repo["v1"]["bonds"]

    def bond_maps(self) -> dict[str, str]:
        """TODO"""

        return self._repo["v1"]["bond_maps"]

    def context(self, name: str) -> v1.deployment.Context:
        """TODO"""

        contexts = self.contexts()

        if name not in contexts:
            raise exceptions.ContextNotFound(name)

        return contexts[name]

    def component(self, name: str) -> v1.component.Component:
        """TODO"""

        components = self.components()

        if name not in components:
            raise exceptions.ComponentTypeNotFound(name)

        return components[name]

    def link(self, name: str) -> v1.link.Link:
        """TODO"""

        links = self.links()

        if name not in links:
            raise exceptions.LinkTypeNotFound(name)

        return links[name]

    def provider(self, name: str) -> v1.provider.Provider:
        """TODO"""

        providers = self.providers()

        if name not in providers:
            raise exceptions.ProviderNotFound(name)

        return providers[name]

    def interface(self, name: str) -> v1.bond.Bond:
        """TODO"""

        interfaces = self.interfaces()

        if name not in interfaces:
            raise exceptions.InterfaceNotFound(name)

        return interfaces[name]

    def bond(self, name: str) -> v1.bond.Bond:
        """TODO"""

        bonds = self.bonds()

        if name not in bonds:
            raise exceptions.BondNotFound(name)

        return bonds[name]

    def provider_for(self, name: str) -> str:
        """TODO"""

        bond_maps = self.bond_maps()

        if name not in bond_maps:
            raise exceptions.BondNotFound(name)

        return bond_maps[name]


def _system_repository() -> list:
    """TODO"""

    entry_points = importlib.metadata.entry_points()

    if "torque" in entry_points:
        return list(entry_points["torque"])

    return []


def _local_repository() -> list:
    """TODO"""

    try:
        importlib.import_module("local")

        return [
            importlib.metadata.EntryPoint(name="local",
                                          value="local:repository",
                                          group="torque")
        ]

    except ModuleNotFoundError:
        return []


def _process_interfaces(_repository: dict[str, object]) -> dict[str, object]:
    """TODO"""

    if "interfaces" not in _repository["v1"]:
        return _repository

    _repository["v1"]["interfaces"] = {
        v1.utils.fqcn(interface): interface
        for interface in _repository["v1"]["interfaces"]
    }

    return _repository


def _process_bonds(_repository: dict[str, object]) -> dict[str, object]:
    """TODO"""

    if "bonds" not in _repository["v1"]:
        return _repository

    for provider_name, provider_bonds in _repository["v1"]["bonds"].items():
        _repository["v1"]["bonds"][provider_name] = {
            v1.utils.fqcn(bond): bond for bond in provider_bonds
        }

    return _repository


def load() -> Repository:
    """TODO"""

    repository = _DEFAULT_REPOSITORY

    entry_points = _system_repository()
    entry_points += _local_repository()

    for entry_point in entry_points:
        # pylint: disable=W0703

        try:
            _repository = entry_point.load()
            _repository = _REPOSITORY_SCHEMA.validate(_repository)

            _repository = _process_interfaces(_repository)
            _repository = _process_bonds(_repository)

            repository = v1.utils.merge_dicts(repository, _repository, False)

        except RuntimeError as exc:
            print(f"WARNING: {entry_point.name}: {exc}", file=sys.stderr)

        except Exception as exc:
            traceback.print_exc()

            print(f"WARNING: {entry_point.name}: unable to load repository: {exc}", file=sys.stderr)

    return Repository(repository)
