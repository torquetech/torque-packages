# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC, abstractmethod

from torque import model
from torque import options


class Component(ABC):
    # pylint: disable=R0903

    """TODO"""

    @staticmethod
    @abstractmethod
    def parameteres() -> list[options.OptionsSpec]:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> list[options.OptionsSpec]:
        """TODO"""

    @staticmethod
    @abstractmethod
    def on_create(dag: model.DAG, component: model.Component):
        """TODO"""

    @staticmethod
    @abstractmethod
    def on_remove(dag: model.DAG, component: model.Component):
        """TODO"""

    @abstractmethod
    def on_build(self):
        """TODO"""


class Link(ABC):
    # pylint: disable=R0903

    """TODO"""

    @staticmethod
    @abstractmethod
    def parameteres() -> list[options.OptionsSpec]:
        """TODO"""

    @staticmethod
    @abstractmethod
    def configuration() -> list[options.OptionsSpec]:
        """TODO"""

    @staticmethod
    @abstractmethod
    def on_create(dag: model.DAG, link: model.Link):
        """TODO"""

    @staticmethod
    @abstractmethod
    def on_remove(dag: model.DAG, link: model.Link):
        """TODO"""

    @abstractmethod
    def on_build(self):
        """TODO"""
