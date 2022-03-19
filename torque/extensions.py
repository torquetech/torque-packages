# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import abc
import importlib
import schema

from torque import dsl
from torque import exceptions
from torque import protocols

from torque.v1 import interfaces


def _is_component(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, interfaces.Component)


def _is_link(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, interfaces.Link)


def _is_protocol(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, interfaces.Protocol)


def _is_dsl_instruction(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, interfaces.DSLInstruction)


def _is_dsl_generator(obj: object) -> bool:
    """TODO"""

    return issubclass(obj, interfaces.DSLGenerator)


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
        schema.Optional("dsl"): {
            schema.Optional(str): {
                schema.Optional(str): _is_dsl_instruction
            }
        },
        schema.Optional("providers"): {
            schema.Optional(str): {
                schema.Optional(str): _is_dsl_generator
            }
        }
    })
}, ignore_extra_keys=True)

_DEFAULT_EXTENSIONS = {
    "v1": {
        "components": {
        },
        "links": {
        },
        "protocols": {
            "file": protocols.FileProtocol
        },
        "dsl": {
            "base": {
                "Service": dsl.Service,
                "Task": dsl.Task
            }
        },
        "providers": {
            # "aws-k8s": {
            #     "Service": ServiceAWS,
            #     "Task": TaskAWS
            # },
            # "docker-compose.dummy_ext": {
            #     "Service": ServiceDockerCompose,
            #     "Task": TaskDockerCompose
            # }
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

    def dsl_extensions(self) -> dict[str, object]:
        """TODO"""

        return self.exts["v1"]["dsl"]

    def component(self, component_type: str) -> interfaces.Component:
        """TODO"""

        _components = self.components()

        if component_type not in _components:
            raise exceptions.ComponentTypeNotFound(component_type)

        return _components[component_type]

    def link(self, link_type: str) -> interfaces.Link:
        """TODO"""

        _links = self.links()

        if link_type not in _links:
            raise exceptions.LinkTypeNotFound(link_type)

        return _links[link_type]

    def protocol(self, protocol: str) -> callable:
        """TODO"""

        _protocols = self.protocols()

        if protocol not in _protocols:
            raise exceptions.ProtocolNotFound(protocol)

        return _protocols[protocol]


def _merge(dict1: dict[str, object], dict2: dict[str, object]) -> dict[str, object]:
    new_dict = {} | dict1

    for key in dict2.keys():
        if isinstance(dict2[key], dict):
            if key in new_dict:
                new_dict[key] = _merge(new_dict[key], dict2[key])

            else:
                new_dict[key] = dict2[key]

        elif issubclass(dict2[key], abc.ABC):
            if key in new_dict:
                raise exceptions.DuplicateExtensionEntry(key)

            new_dict[key] = dict2[key]

        else:
            assert False

    return new_dict


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
                extensions = _merge(extensions, extension)

            except exceptions.DuplicateExtensionEntry as exc:
                print(f"WARNING: {entry_point.name}({exc}): duplicate entry")

            except Exception as exc:
                print(f"WARNING: {entry_point.name}: unable to load extension: {exc}")

    return Extensions(extensions)
