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


def _is_component(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, v1.component.Component)


def _is_link(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, v1.link.Link)


def _is_protocol(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, v1.protocol.Protocol)


def _is_provider(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, v1.provider.Provider)


def _is_interface(obj: object) -> bool:
    """TODO"""

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
        v1.schema.Optional("interfaces"): {
            v1.schema.Optional(str): {
                v1.schema.Optional(str): _is_interface
            }
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
        "interfaces": {
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
        interfaces = {}

        for provider_name, provider_class in self._repo["v1"]["providers"].items():
            # pylint: disable=W0212

            providers[provider_name] = provider_class
            provider_class._TORQUE_INTERFACES = []

        for provider_name, provider_interfaces in self._repo["v1"]["interfaces"].items():
            provider_class = self.provider(provider_name)

            for interface_name, interface_class in provider_interfaces.items():
                interface_name = f"{provider_name}/{interface_name}"

                interface_class._TORQUE_PROVIDER = provider_name
                interface_class._TORQUE_NAME = interface_name

                provider_class._TORQUE_INTERFACES.append(interface_name)

                interfaces[interface_name] = interface_class

        self._repo["v1"]["providers"] = providers
        self._repo["v1"]["interfaces"] = interfaces

    def components(self) -> dict[str, v1.component.Component]:
        """TODO"""

        return self._repo["v1"]["components"]

    def links(self) -> dict[str, v1.link.Link]:
        """TODO"""

        return self._repo["v1"]["links"]

    def protocols(self) -> dict[str, v1.protocol.Protocol]:
        """TODO"""

        return self._repo["v1"]["protocols"]

    def providers(self) -> dict[str, v1.provider.Provider]:
        """TODO"""

        return self._repo["v1"]["providers"]

    def interfaces(self) -> dict[str, v1.provider.Interface]:
        """TODO"""

        return self._repo["v1"]["interfaces"]

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


def _system_repository():
    """TODO"""

    entry_points = importlib.metadata.entry_points()

    if "torque" in entry_points:
        return list(entry_points["torque"])

    return []


def _local_repository():
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

            repository = v1.utils.merge_dicts(repository, _repository, False)

        except RuntimeError as exc:
            print(f"WARNING: {entry_point.name}: {exc}", file=sys.stderr)

        except Exception as exc:
            traceback.print_exc()

            print(f"WARNING: {entry_point.name}: unable to load repository: {exc}", file=sys.stderr)

    return Repository(repository)
