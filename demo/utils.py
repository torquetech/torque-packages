# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import threading
import typing


def load_file(name: str) -> str:
    """TODO"""

    with open(name, encoding="utf8") as file:
        return file.read().strip()


def module_path() -> str:
    """TODO"""

    return os.path.dirname(__file__)


def normalize(name: str) -> str:
    """TODO"""

    name = name.replace("_", "-")
    name = name.replace(".", "-")

    return name


T = typing.TypeVar("T")

class Future(typing.Generic[T]):
    """TODO"""

    def __init__(self, value=None):
        self._condition = threading.Condition()
        self._value = value

    def get(self):
        """TODO"""

        with self._condition:
            while self._value is None:
                self._condition.wait()

            while callable(self._value):
                self._value = self._value()

            return self._value

    def set(self, value: object):
        """TODO"""

        with self._condition:
            assert self._value is None

            self._value = value
            self._condition.notify_all()
