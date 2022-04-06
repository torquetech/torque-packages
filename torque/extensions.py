# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import importlib
import traceback
import sys

import schema

from torque import exceptions
from torque import links
from torque import protocols
from torque import utils

from torque.v1 import component as component_v1
from torque.v1 import link as link_v1
from torque.v1 import protocol as protocol_v1
from torque.v1 import provider as provider_v1


def _is_component(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, component_v1.Component)


def _is_link(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, link_v1.Link)


def _is_protocol(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, protocol_v1.Protocol)


def _is_provider(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, provider_v1.Provider)


_EXTENSION_SCHEMA = schema.Schema({
    schema.Optional("v1"): schema.Schema({
        schema.Optional("components"): {
            schema.Optional(str): _is_component
        },
        schema.Optional("links"): {
            schema.Optional(str): _is_link
        },
        schema.Optional("protocols"): {
            schema.Optional(str): _is_protocol
        },
        schema.Optional("providers"): {
            schema.Optional(str): _is_provider
        }
    })
}, ignore_extra_keys=True)

_DEFAULT_EXTENSIONS = {
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
        }
    }
}


class Extensions:
    """TODO"""

    def __init__(self, exts: dict[str, object]):
        self.exts = exts

    def components(self) -> dict[str, object]:
        """TODO"""

        return self.exts["v1"]["components"]

    def links(self) -> dict[str, object]:
        """TODO"""

        return self.exts["v1"]["links"]

    def protocols(self) -> dict[str, object]:
        """TODO"""

        return self.exts["v1"]["protocols"]

    def providers(self) -> dict[str, object]:
        """TODO"""

        return self.exts["v1"]["providers"]

    def component(self, component_type: str) -> component_v1.Component:
        """TODO"""

        components = self.components()

        if component_type not in components:
            raise exceptions.ComponentTypeNotFound(component_type)

        return components[component_type]

    def link(self, link_type: str) -> link_v1.Link:
        """TODO"""

        links = self.links()

        if link_type not in links:
            raise exceptions.LinkTypeNotFound(link_type)

        return links[link_type]

    def protocol(self, protocol: str) -> protocol_v1.Protocol:
        """TODO"""

        protocols = self.protocols()

        if protocol not in protocols:
            raise exceptions.ProtocolNotFound(protocol)

        return protocols[protocol]

    def provider(self, provider: str) -> provider_v1.Provider:
        """TODO"""

        providers = self.providers()

        if provider not in providers:
            raise exceptions.ProviderNotFound(provider)

        return providers[provider]


def load() -> Extensions:
    """TODO"""

    entry_points = importlib.metadata.entry_points()
    extensions = _DEFAULT_EXTENSIONS

    if "torque" in entry_points:
        entry_points = entry_points["torque"]

        for entry_point in entry_points:
            # pylint: disable=W0703

            try:
                extension = entry_point.load()

                extension = _EXTENSION_SCHEMA.validate(extension)
                extensions = utils.merge_dicts(extensions, extension, False)

            except exceptions.DuplicateDictEntry as exc:
                print(f"WARNING: {entry_point.name}({exc}): duplicate entry", file=sys.stderr)

            except Exception as exc:
                traceback.print_exc()

                print(f"WARNING: {entry_point.name}: unable to load extension: {exc}", file=sys.stderr)

    return Extensions(extensions)
