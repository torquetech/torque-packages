# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from copy import deepcopy

import pydot

from torque import exceptions


class Component:
    """TODO"""

    def __init__(self,
                 name: str,
                 type: str,
                 parameters: object):
        # pylint: disable=W0622

        self.name = name
        self.type = type
        self.parameters = parameters

        self.inbound_links: dict[str, set()] = {}
        self.outbound_links: dict[str, set()] = {}

    def __repr__(self) -> str:
        inbound_links = ",".join(self.inbound_links)
        outbound_links = ",".join(self.outbound_links)

        return f"Component({self.name}" \
               f", type={self.type}" \
               f", inbound_links=[{inbound_links}]" \
               f", outbound_links=[{outbound_links}])"

    def add_inbound_link(self, component: str, link: str):
        """TODO"""

        if component not in self.inbound_links:
            self.inbound_links[component] = set()

        self.inbound_links[component].add(link)

    def remove_inbound_link(self, component: str, link: str):
        """TODO"""

        if component not in self.inbound_links:
            raise exceptions.ComponentsNotConnected(component, self.name)

        inbound_links = self.inbound_links[component]

        if link not in inbound_links:
            raise exceptions.ComponentsNotConnected(component, self.name)

        inbound_links.remove(link)

        if not inbound_links:
            self.inbound_links.pop(component)

    def add_outbound_link(self, component: str, link: str):
        """TODO"""

        if component not in self.outbound_links:
            self.outbound_links[component] = set()

        self.outbound_links[component].add(link)

    def remove_outbound_link(self, component: str, link: str):
        """TODO"""

        if component not in self.outbound_links:
            raise exceptions.ComponentsNotConnected(self.name, component)

        outbound_links = self.outbound_links[component]

        if link not in outbound_links:
            raise exceptions.ComponentsNotConnected(self.name, component)

        outbound_links.remove(link)

        if not outbound_links:
            self.outbound_links.pop(component)


class Link:
    """TODO"""

    def __init__(self,
                 name: str,
                 type: str,
                 source: str,
                 destination: str,
                 parameters: object):
        # pylint: disable=R0913,W0622

        self.name = name
        self.type = type
        self.source = source
        self.destination = destination
        self.parameters = parameters

    def __repr__(self) -> str:
        return f"Link({self.name}" \
               f", type={self.type}" \
               f", source={self.source}" \
               f", destination={self.destination})"


class DAG:
    """TODO"""

    def __init__(self, revision: int):
        self.revision = revision
        self.components = {}
        self.links = {}

    def create_component(self,
                         name: str,
                         type: str,
                         parameters: object) -> Component:
        # pylint: disable=W0622

        """TODO"""

        if name in self.components:
            raise exceptions.ComponentExists(name)

        component = Component(name, type, parameters)

        self.components[name] = component
        return component

    def get_component(self, name: str) -> Component:
        """TODO"""

        if name not in self.components:
            raise exceptions.ComponentNotFound(name)

        return self.components[name]

    def remove_component(self, name: str) -> Component:
        """TODO"""

        component = self.get_component(name)

        if component.inbound_links:
            raise exceptions.ComponentStillConnected(name)

        if component.outbound_links:
            raise exceptions.ComponentStillConnected(name)

        return self.components.pop(name)

    def create_link(self,
                    name: str,
                    type: str,
                    source: str,
                    destination: str,
                    parameters: object) -> Link:
        # pylint: disable=R0913,W0622

        """TODO"""

        if name in self.links:
            raise exceptions.LinkExists(name)

        if source == destination:
            raise exceptions.CycleDetected()

        if source not in self.components:
            raise exceptions.ComponentNotFound(source)

        if destination not in self.components:
            raise exceptions.ComponentNotFound(destination)

        link = Link(name, type, source, destination, parameters)

        self.components[destination].add_inbound_link(source, name)
        self.components[source].add_outbound_link(destination, name)

        self.links[name] = link
        return link

    def get_link(self, name: str) -> Component:
        """TODO"""

        if name not in self.links:
            raise exceptions.LinkNotFound(name)

        return self.links[name]

    def remove_link(self, name: str) -> Link:
        """TODO"""

        link = self.get_link(name)

        self.components[link.destination].remove_inbound_link(link.source, name)
        self.components[link.source].remove_outbound_link(link.destination, name)

        return self.links.pop(name)

    def _dfs_check(self,
                   visited_components: set[str],
                   seen_components: set[str],
                   component: str) -> bool:
        """TODO"""

        if component in seen_components:
            raise exceptions.CycleDetected()

        seen_components.add(component)
        visited_components.add(component)

        for child_component in self.components[component].outbound_links:
            self._dfs_check(visited_components, seen_components, child_component)

        seen_components.remove(component)

    def verify(self) -> bool:
        """TODO"""

        seen_components: set[str] = set()
        visited_components: set[str] = set()

        for root in self.components:
            if root in visited_components:
                continue

            self._dfs_check(visited_components, seen_components, root)

    def used_component_types(self) -> set[str]:
        """TODO"""

        return {i.type for i in self.components.values()}

    def used_link_types(self) -> set[str]:
        """TODO"""

        return {i.type for i in self.links.values()}

    def subset(self, components: [str]) -> "DAG":
        """TODO"""

        subset = deepcopy(self)

        if components is None:
            return subset

        components_to_keep = set()
        links_to_keep = set()

        while len(components) != 0:
            component = subset.components[components.pop()]

            if component.name not in components_to_keep:
                components_to_keep.add(component.name)

                for component_name, inbound_links in component.inbound_links.items():
                    components.append(component_name)

                    for link in inbound_links:
                        links_to_keep.add(link)

        components_to_remove = set(subset.components.keys()) - components_to_keep
        links_to_remove = set(subset.links.keys()) - links_to_keep

        for component_name in components_to_remove:
            subset.components.pop(component_name)

        for link_name in links_to_remove:
            subset.links.pop(link_name)

        for component in subset.components.values():
            for component_name in components_to_remove:
                component.inbound_links.pop(component_name, None)
                component.outbound_links.pop(component_name, None)

        return subset

    def dot(self, name: str) -> str:
        """TODO"""

        graph = pydot.Dot(name, graph_type="digraph")

        for component in self.components.values():
            node = pydot.Node(component.name, label=component.name)
            graph.add_node(node)

        for link in self.links.values():
            edge = pydot.Edge(link.source, link.destination)
            graph.add_edge(edge)

        return graph.to_string()
