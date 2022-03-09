# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import exceptions
from torque import options


Types = dict[str, object]


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

    def __init__(self,
                 name: str,
                 source: str,
                 destination: str,
                 link_type: str,
                 params: options.Options):
        # pylint: disable=R0913

        self.name = name
        self.source = source
        self.destination = destination
        self.link_type = link_type
        self.params = params
        self.config = None

    def __repr__(self) -> str:
        return f"Link({self.name}" \
               f", source={self.source}" \
               f", destination={self.destination}" \
               f", link_type={self.link_type})"


class Component:
    """TODO"""

    def __init__(self,
                 name: str,
                 cluster: str,
                 component_type: str,
                 params: options.Options):
        self.name = name
        self.cluster = cluster
        self.component_type = component_type
        self.params = params
        self.config = None

        self.inbound_links: dict[str, str] = {}
        self.outbound_links: dict[str, str] = {}

    def __repr__(self) -> str:
        inbound_links = ",".join(self.inbound_links)
        outbound_links = ",".join(self.outbound_links)

        return f"Component({self.name}" \
               f", cluster={self.cluster}" \
               f", inbound_links=[{inbound_links}]" \
               f", outbound_links=[{outbound_links}]" \
               f", component_type={self.component_type})"

    def add_inbound_link(self, component: str, link: str):
        """TODO"""

        if component in self.inbound_links:
            raise exceptions.ComponentsAlreadyConnected(component, self.name)

        self.inbound_links[component] = link

    def remove_inbound_link(self, component: str):
        """TODO"""

        if component not in self.inbound_links:
            raise exceptions.ComponentsNotConnected(component, self.name)

        self.inbound_links.pop(component)

    def add_outbound_link(self, component: str, link: str):
        """TODO"""

        if component in self.outbound_links:
            raise exceptions.ComponentsAlreadyConnected(self.name, component)

        self.outbound_links[component] = link

    def remove_outbound_link(self, component: str):
        """TODO"""

        if component not in self.outbound_links:
            raise exceptions.ComponentsNotConnected(self.name, component)

        self.outbound_links.pop(component)


class DAG:
    """TODO"""

    def __init__(self, revision: int, types: Types):
        self.revision = revision
        self.clusters = {}
        self.components = {}
        self.links = {}
        self.types = types

    def create_cluster(self, name: str) -> Cluster:
        """TODO"""

        if name in self.clusters:
            raise exceptions.ClusterExists(name)

        cluster = Cluster(name)

        self.clusters[name] = cluster
        return cluster

    def remove_cluster(self, name: str) -> Cluster:
        """TODO"""

        if name not in self.clusters:
            raise exceptions.ClusterNotFound(name)

        clusters_in_use = {i.cluster for i in self.components.values()}

        if name in clusters_in_use:
            raise exceptions.ClusterNotEmpty(name)

        return self.clusters.pop(name)

    def create_component(self,
                         name: str,
                         cluster: str,
                         component_type: str,
                         params: dict[str, str]) -> Component:
        """TODO"""

        if name in self.components:
            raise exceptions.ComponentExists(name)

        if cluster not in self.clusters:
            raise exceptions.ClusterNotFound(cluster)

        types = self.types["components.v1"]

        if component_type not in types:
            raise exceptions.ComponentTypeNotFound(component_type)

        params = options.process(types[component_type].parameters, params)
        component = Component(name, cluster, component_type, params)

        self.components[name] = component
        return component

    def remove_component(self, name: str) -> Component:
        """TODO"""

        if name not in self.components:
            raise exceptions.ComponentNotFound(name)

        component = self.components[name]

        if len(component.inbound_links) != 0:
            raise exceptions.ComponentStillConnected(name)

        if len(component.outbound_links) != 0:
            raise exceptions.ComponentStillConnected(name)

        return self.components.pop(name)

    def create_link(self,
                    name: str,
                    source: str,
                    destination: str,
                    link_type: str,
                    params: dict[str, str]) -> Link:
        # pylint: disable=R0913

        """TODO"""

        if name in self.links:
            raise exceptions.LinkExists(name)

        if source == destination:
            raise exceptions.CycleDetected(name)

        if source not in self.components:
            raise exceptions.ComponentNotFound(source)

        if destination not in self.components:
            raise exceptions.ComponentNotFound(destination)

        types = self.types["links.v1"]

        if link_type not in types:
            raise exceptions.LinkTypeNotFound(link_type)

        params = options.process(types[link_type].parameters, params)
        link = Link(name, source, destination, link_type, params)

        self.components[destination].add_inbound_link(source, name)
        self.components[source].add_outbound_link(destination, name)

        self.links[name] = link
        return link

    def remove_link(self, name: str) -> Link:
        """TODO"""

        if name not in self.links:
            raise exceptions.LinkNotFound(name)

        link = self.links[name]

        self.components[link.destination].remove_inbound_link(link.source)
        self.components[link.source].remove_outbound_link(link.destination)

        return self.links.pop(name)

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

    def _has_cycles(self) -> bool:
        """TODO"""

        seen_components: set[str] = set()
        visited_components: set[str] = set()

        for root in self.components:
            if root in visited_components:
                continue

            if self._dfs_check(visited_components, seen_components, root):
                return True

        return False

    def verify(self):
        """TODO"""

        if self._has_cycles():
            raise exceptions.CycleDetected()

    def used_component_types(self) -> set[str]:
        """TODO"""

        return {i.component_type for i in self.components.values()}

    def used_link_types(self) -> set[str]:
        """TODO"""

        return {i.link_type for i in self.links.values()}
