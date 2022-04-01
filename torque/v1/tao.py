# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class Statement:
    """TODO"""


class Service(Statement):
    """TODO"""

    def __init__(self, name: str, image: str):
        # pylint: disable=W0613

        self.name = name
        self.image = image


class Task(Statement):
    """TODO"""

    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image


def fqcn(instance: type) -> str:
    """TODO"""

    return f"{instance.__class__.__module__}.{instance.__class__.__name__}"
