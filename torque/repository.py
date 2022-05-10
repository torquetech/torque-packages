# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import importlib
import traceback
import sys

from torque import exceptions
from torque import links
from torque import protocols
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


def _is_protocol(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.protocol.Protocol)


def _is_provider(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.provider.Provider)


def _is_interface(obj: type) -> bool:
    """TODO"""

    if not isinstance(obj, type):
        return False

    return issubclass(obj, v1.provider.Interface)


_REPOSITORY_SCHEMA = v1.schema.Schema({
    v1.schema.Optional("v1"): v1.schema.Schema({
        v1.schema.Optional("components"): {
            v1.schema.Optional(str): _is_component
        },
        v1.schema.Optional("links"): {
            v1.schema.Optional(str): _is_link
        },
        v1.schema.Optional("protocols"): {
            v1.schema.Optional(str): _is_protocol
        },
        v1.schema.Optional("providers"): {
            v1.schema.Optional(str): _is_provider
        },
        v1.schema.Optional("interfaces"): [
            _is_interface
        ],
        v1.schema.Optional("binds"): {
            v1.schema.Optional(str): [
                _is_interface
            ]
        }
    })
}, ignore_extra_keys=True)

_DEFAULT_REPOSITORY = {
    "v1": {
        "components": {
        },
        "links": {
            "torquetech.dev/dependency": links.DependencyLink
        },
        "protocols": {
            "file": protocols.FileProtocol
        },
        "providers": {
        },
        "binds": {
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
        binds = {}
        bind_maps = {}

        for provider_name, provider_class in self._repo["v1"]["providers"].items():
            providers[provider_name] = provider_class

        for provider_name, provider_binds in self._repo["v1"]["binds"].items():
            for bind_name, bind_class in provider_binds.items():
                binds[bind_name] = bind_class
                bind_maps[bind_name] = provider_name

        self._repo["v1"]["providers"] = providers
        self._repo["v1"]["binds"] = binds
        self._repo["v1"]["bind_maps"] = bind_maps

    def components(self) -> dict:
        """TODO"""

        return self._repo["v1"]["components"]

    def links(self) -> dict:
        """TODO"""

        return self._repo["v1"]["links"]

    def protocols(self) -> dict:
        """TODO"""

        return self._repo["v1"]["protocols"]

    def providers(self) -> dict:
        """TODO"""

        return self._repo["v1"]["providers"]

    def interfaces(self) -> dict:
        """TODO"""

        return self._repo["v1"]["interfaces"]

    def binds(self) -> dict:
        """TODO"""

        return self._repo["v1"]["binds"]

    def bind_maps(self) -> dict:
        """TODO"""

        return self._repo["v1"]["bind_maps"]

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

    def protocol(self, name: str) -> v1.protocol.Protocol:
        """TODO"""

        protocols = self.protocols()

        if name not in protocols:
            raise exceptions.ProtocolNotFound(name)

        return protocols[name]

    def provider(self, name: str) -> v1.provider.Provider:
        """TODO"""

        providers = self.providers()

        if name not in providers:
            raise exceptions.ProviderNotFound(name)

        return providers[name]

    def interface(self, name: str) -> v1.provider.Interface:
        """TODO"""

        interfaces = self.interfaces()

        if name not in interfaces:
            raise exceptions.InterfaceNotFound(name)

        return interfaces[name]

    def bind(self, name: str) -> v1.provider.Interface:
        """TODO"""

        binds = self.binds()

        if name not in binds:
            raise exceptions.BindNotFound(name)

        return binds[name]

    def provider_for(self, name: str) -> str:
        """TODO"""

        bind_maps = self.bind_maps()

        if name not in bind_maps:
            raise exceptions.BindNotFound(name)

        return bind_maps[name]


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


def _process_interfaces(_repository: dict) -> dict:
    """TODO"""

    if "interfaces" not in _repository["v1"]:
        return _repository

    _repository["v1"]["interfaces"] = {
        v1.utils.fqcn(interface): interface
        for interface in _repository["v1"]["interfaces"]
    }

    return _repository


def _process_binds(_repository: dict) -> dict:
    """TODO"""

    if "binds" not in _repository["v1"]:
        return _repository

    for provider_name, provider_binds in _repository["v1"]["binds"].items():
        _repository["v1"]["binds"][provider_name] = {
            v1.utils.fqcn(bind): bind for bind in provider_binds
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
            _repository = _process_binds(_repository)

            repository = v1.utils.merge_dicts(repository, _repository, False)

        except RuntimeError as exc:
            print(f"WARNING: {entry_point.name}: {exc}", file=sys.stderr)

        except Exception as exc:
            traceback.print_exc()

            print(f"WARNING: {entry_point.name}: unable to load repository: {exc}", file=sys.stderr)

    return Repository(repository)
