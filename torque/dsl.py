# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import interfaces


class Service(interfaces.DSLInstruction):
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str, image: str, *args, **kwargs):
        # pylint: disable=W0613

        self.name = name
        self.image = image


class Task(interfaces.DSLInstruction):
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str, image: str, *args, **kwargs):
        # pylint: disable=W0613

        self.name = name
        self.image = image
