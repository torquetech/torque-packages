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
        "required": bool,
        v1.schema.Optional("bind_to"): v1.schema.Or("source", "destination", "provider")
    }
})


def _bind_to(type: object,
             name: str,
             labels: [str],
             get_bond: typing.Callable) -> object:
    """TODO"""

    bonds = types.SimpleNamespace()
    requirements = type.on_requirements()

    if not requirements:
        return bonds

    requirements = _REQUIREMENTS_SCHEMA.validate(requirements)

    for r_name, r in requirements.items():
        if "bind_to" in r and r["bind_to"] != "provider":
            raise exceptions.InvalidRequirement(v1.utils.fqcn(type))

        if not issubclass(r["interface"], v1.bond.Bond):
            raise exceptions.InvalidRequirement(v1.utils.fqcn(type))

        bond = get_bond(r["interface"],
                        r["required"],
                        name,
                        labels)

        setattr(bonds, r_name, bond)

    return bonds


def bind_to_provider(type: object,
                     name: str,
                     labels: [str],
                     get_bond: typing.Callable) -> object:
    """TODO"""

    return _bind_to(type, name, labels, get_bond)


def bind_to_component(type: object,
                      name: str,
                      labels: [str],
                      get_bond: typing.Callable) -> object:
    """TODO"""

    return _bind_to(type, name, labels, get_bond)


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
        if "bind_to" not in r:
            raise exceptions.InvalidRequirement(v1.utils.fqcn(type))

        bond = None

        if issubclass(r["interface"], v1.component.Interface):
            if r["bind_to"] == "source":
                # pylint: disable=W0212
                bond = source._torque_interface(r["interface"],
                                                r["required"])

            elif r["bind_to"] == "destination":
                # pylint: disable=W0212
                bond = destination._torque_interface(r["interface"],
                                                     r["required"])

        elif issubclass(r["interface"], v1.bond.Bond):
            if r["bind_to"] != "provider":
                raise exceptions.InvalidRequirement(v1.utils.fqcn(type))

            bond = get_bond(r["interface"],
                            r["required"],
                            name,
                            source,
                            destination)

        else:
            raise exceptions.InvalidRequirement(v1.utils.fqcn(type))

        setattr(bonds, r_name, bond)

    return bonds
