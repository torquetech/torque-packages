# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import typing
import types

from torque import exceptions
from torque import model
from torque import v1


_REQUIREMENTS_SCHEMA = v1.schema.Schema({
    v1.schema.Optional(str): {
        "interface": type,
        "required": bool
    }
})


def _bind_to(type: object,
             name: str,
             get_bond: typing.Callable) -> object:
    """TODO"""

    bonds = types.SimpleNamespace()
    requirements = type.on_requirements()

    if not requirements:
        return bonds

    requirements = _REQUIREMENTS_SCHEMA.validate(requirements)

    for r_name, r in requirements.items():
        if not issubclass(r["interface"], v1.bond.Interface):
            raise exceptions.InvalidRequirement(name)

        bond = get_bond(r["interface"],
                        r["required"],
                        name)

        setattr(bonds, r_name, bond)

    return bonds


def bind_to_provider(type: object,
                     name: str,
                     get_bond: typing.Callable) -> object:
    """TODO"""

    return _bind_to(type, name, get_bond)


def bind_to_component(type: object,
                      name: str,
                      get_bond: typing.Callable) -> object:
    """TODO"""

    return _bind_to(type, name, get_bond)


def bind_to_link(type: object,
                 name: str,
                 source: model.Component,
                 destination: model.Component,
                 get_bond: typing.Callable) -> object:
    """TODO"""

    bonds = types.SimpleNamespace()
    requirements = type.on_requirements()

    if not requirements:
        return bonds

    requirements = _REQUIREMENTS_SCHEMA.validate(requirements)

    for r_name, r in requirements.items():
        bond = None

        if issubclass(r["interface"], v1.component.SourceInterface):
            # pylint: disable=W0212
            bond = source._torque_interface(r["interface"],
                                            r["required"])

        elif issubclass(r["interface"], v1.component.DestinationInterface):
            # pylint: disable=W0212
            bond = destination._torque_interface(r["interface"],
                                                 r["required"])

        elif issubclass(r["interface"], v1.bond.Interface):
            bond = get_bond(r["interface"],
                            r["required"],
                            name,
                            source,
                            destination)

        else:
            raise exceptions.InvalidRequirement(name)

        setattr(bonds, r_name, bond)

    return bonds
