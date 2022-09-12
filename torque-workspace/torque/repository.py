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

    if obj is None:
        return True

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
        v1.schema.Optional("contexts"): [
            _is_context
        ],
        v1.schema.Optional("components"): [
            _is_component
        ],
        v1.schema.Optional("links"): [
            _is_link
        ],
        v1.schema.Optional("providers"): [
            _is_provider
        ],
        v1.schema.Optional("interfaces"): [
            _is_bond
        ],
        v1.schema.Optional("bonds"): {
            _is_provider: [_is_bond]
        }
    })
}, ignore_extra_keys=True)

_DEFAULT_REPOSITORY = {
    "v1": {
        "contexts": {
            v1.utils.fqcn(defaults.LocalContext): defaults.LocalContext
        },
        "components": {},
        "links": {
            v1.utils.fqcn(defaults.DependencyLink): defaults.DependencyLink
        },
        "providers": {},
        "interfaces": {},
        "bonds": {}
    }
}


class Repository:
    """TODO"""

    def __init__(self, repo: dict[str, object]):
        self._repo = repo

        self._process_bonds()

    def _process_bonds(self):
        """TODO"""

        bonds = {}
        bond_maps = {}

        for provider_name, provider_bonds in self._repo["v1"]["bonds"].items():
            for bond_name, bond_type in provider_bonds.items():
                bonds[bond_name] = bond_type
                bond_maps[bond_name] = provider_name

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


def _process_items(repository: dict[str, object], name: str) -> dict[str, object]:
    """TODO"""

    if name not in repository["v1"]:
        return repository

    repository["v1"][name] = {
        v1.utils.fqcn(item): item
        for item in repository["v1"][name]
    }

    return repository


def _process_bonds(repository: dict[str, object]) -> dict[str, object]:
    """TODO"""

    if "bonds" not in repository["v1"]:
        return repository

    bonds = {}

    for provider_type, provider_bonds in repository["v1"]["bonds"].items():
        provider_name = v1.utils.fqcn(provider_type)

        bonds[provider_name] = {
            v1.utils.fqcn(bond): bond for bond in provider_bonds
        }

    repository["v1"]["bonds"] = bonds

    return repository


def load() -> Repository:
    """TODO"""

    repository = {} | _DEFAULT_REPOSITORY

    entry_points = _system_repository()
    entry_points += _local_repository()

    for entry_point in entry_points:
        # pylint: disable=W0703

        try:
            package_repository = entry_point.load()
            package_repository = _REPOSITORY_SCHEMA.validate(package_repository)

            package_repository = _process_items(package_repository, "contexts")
            package_repository = _process_items(package_repository, "components")
            package_repository = _process_items(package_repository, "links")
            package_repository = _process_items(package_repository, "providers")
            package_repository = _process_items(package_repository, "interfaces")
            package_repository = _process_bonds(package_repository)

            repository = v1.utils.merge_dicts(repository, package_repository)

        except Exception as exc:
            traceback.print_exc()

            print(f"WARNING: {entry_point.name}: unable to load repository: {exc}", file=sys.stderr)

    return Repository(repository)
