# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class Instruction:
    """TODO"""


class Service(Instruction):
    """TODO"""

    def __init__(self, name: str, image: str):
        # pylint: disable=W0613

        self.name = name
        self.image = image


class Task(Instruction):
    """TODO"""

    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image


def fqcn(instruction: Instruction) -> str:
    """TODO"""
    assert issubclass(type(instruction), Instruction)
    return f"{instruction.__class__.__module__}.{instruction.__class__.__name__}"
