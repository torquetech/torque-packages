# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from abc import ABC, abstractmethod
from collections import namedtuple

from torque.exceptions import DuplicateCluster
from torque.exceptions import DuplicateComponent
from torque.exceptions import DuplicateLink
from torque.exceptions import ClusterNotFound
from torque.exceptions import CycleDetected
from torque.exceptions import ComponentNotFound
from torque.exceptions import LinkAlreadyExists


Parameter = namedtuple("Parameter", ["name", "description", "default_value"])
Option = namedtuple("Option", ["name", "description", "default_value"])


class ComponentType(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: list[Parameter] = []
    options: list[Option] = []

    @abstractmethod
    def on_build(self):
        """TODO"""


class LinkType(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: list[Parameter] = []
    options: list[Option] = []

    @abstractmethod
    def on_build(self):
        """TODO"""


class Cluster:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Cluster({self.name})"


class Link:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str, source: str, destination: str, link_type: str):
        self.name = name
        self.source = source
        self.destination = destination
        self.link_type = link_type

    def __repr__(self) -> str:
        return f"Link({self.name}" \
               f", source={self.source.name}" \
               f", destination={self.destination.name}" \
               f", link_type={self.link_type})"


class Component:
    """TODO"""

    def __init__(self, name: str, cluster: str, component_type: str):
        self.name = name
        self.cluster = cluster
        self.component_type = component_type

        self.inbound_links: dict[str, str] = {}
        self.outbound_links: dict[str, str] = {}

    def __repr__(self) -> str:
        inbound_links = ",".join(self.inbound_links)
        outbound_links = ",".join(self.outbound_links)

        return f"Component({self.name}" \
               f", cluster={self.cluster.name}" \
               f", inbound_links=[{inbound_links}]" \
               f", outbound_links=[{outbound_links}]" \
               f", component_type={self.component_type})"

    def add_inbound_link(self, component: str, link: str):
        """TODO"""

        if component in self.inbound_links:
            raise LinkAlreadyExists(component, self.name)

        self.inbound_links[component] = link

    def add_outbound_link(self, component: str, link: str):
        """TODO"""

        if component in self.outbound_links:
            raise LinkAlreadyExists(self.name, component)

        self.outbound_links[component] = link


class DAG:
    """TODO"""

    def __init__(self):
        self.clusters = {}
        self.components = {}
        self.links = {}

    def create_cluster(self, name: str):
        """TODO"""

        if name in self.clusters:
            raise DuplicateCluster(name)

        self.clusters[name] = Cluster(name)

    def create_component(self, name: str, cluster: str, component_type: str):
        """TODO"""

        if name in self.components:
            raise DuplicateComponent(name)

        if cluster not in self.clusters:
            raise ClusterNotFound(cluster)

        self.components[name] = Component(name, cluster, component_type)

    def create_link(self, name: str, source: str, destination: str, link_type: str):
        """TODO"""

        if name in self.links:
            raise DuplicateLink(name)

        if source == destination:
            raise CycleDetected(name)

        if source not in self.components:
            raise ComponentNotFound(source)

        if destination not in self.components:
            raise ComponentNotFound(destination)

        self.links[name] = Link(name, source, destination, link_type)

        self.components[destination].add_inbound_link(source, name)
        self.components[source].add_outbound_link(destination, name)

    def _dfs_check(self,
                   visited_components: set[str],
                   seen_components: set[str],
                   component: str) -> bool:
        """TODO"""

        if component in seen_components:
            return True

        seen_components.add(component)
        visited_components.add(component)

        for child_component in self.components[component].outbound_links:
            if self._dfs_check(visited_components, seen_components, child_component):
                return True

        seen_components.remove(component)

        return False

    def has_cycles(self) -> bool:
        """TODO"""

        seen_components: set[str] = set()
        visited_components: set[str] = set()

        for root in self.components:
            if root in visited_components:
                continue

            if self._dfs_check(visited_components, seen_components, root):
                return True

        return False
