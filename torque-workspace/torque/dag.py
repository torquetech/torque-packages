# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import re

from copy import deepcopy

import pydot

from torque import exceptions


_FILTER = re.compile(r"^\s*([a-z0-9.\-_/]+)\s*(=|!=|~=|~!)\s*(.*)$")


class Component:
    """DOCSTRING"""

    def __init__(self,
                 name: str,
                 type: str,
                 parameters: dict[str, str],
                 labels: dict[str, str]):
        # pylint: disable=W0622

        self.name = name
        self.type = type
        self.parameters = parameters
        self.labels = labels

        self.inbound_links: dict[str, set()] = {}
        self.outbound_links: dict[str, set()] = {}

    def describe(self) -> dict[str, object]:
        """DOCSTRING"""

        inbound_links = []
        outbound_links = []

        for component, links in self.inbound_links.items():
            for link in links:
                inbound_links.append({link: component})

        for component, links in self.outbound_links.items():
            for link in links:
                outbound_links.append({link: component})

        return {
            "name": self.name,
            "type": self.type,
            "parameters": self.parameters,
            "labels": [
                f"{key}={value}" for key, value in self.labels.items()
            ],
            "inbound_links": inbound_links,
            "outbound_links": outbound_links
        }

    def add_inbound_link(self, component: str, link: str):
        """DOCSTRING"""

        if component not in self.inbound_links:
            self.inbound_links[component] = set()

        self.inbound_links[component].add(link)

    def remove_inbound_link(self, component: str, link: str):
        """DOCSTRING"""

        if component not in self.inbound_links:
            raise exceptions.ComponentsNotConnected(component, self.name)

        inbound_links = self.inbound_links[component]

        if link not in inbound_links:
            raise exceptions.ComponentsNotConnected(component, self.name)

        inbound_links.remove(link)

        if not inbound_links:
            self.inbound_links.pop(component)

    def add_outbound_link(self, component: str, link: str):
        """DOCSTRING"""

        if component not in self.outbound_links:
            self.outbound_links[component] = set()

        self.outbound_links[component].add(link)

    def remove_outbound_link(self, component: str, link: str):
        """DOCSTRING"""

        if component not in self.outbound_links:
            raise exceptions.ComponentsNotConnected(self.name, component)

        outbound_links = self.outbound_links[component]

        if link not in outbound_links:
            raise exceptions.ComponentsNotConnected(self.name, component)

        outbound_links.remove(link)

        if not outbound_links:
            self.outbound_links.pop(component)


class Link:
    """DOCSTRING"""

    def __init__(self,
                 name: str,
                 type: str,
                 source: str,
                 destination: str,
                 parameters: dict[str, str],
                 labels: dict[str, str]):
        # pylint: disable=R0913,W0622

        self.name = name
        self.type = type
        self.source = source
        self.destination = destination
        self.parameters = parameters
        self.labels = labels

    def describe(self) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "name": self.name,
            "type": self.type,
            "source": self.source,
            "destination": self.destination,
            "parameters": self.parameters,
            "labels": [
                f"{key}={value}" for key, value in self.labels.items()
            ]
        }


def _eval_filter(filter: str, labels: dict[str, str]):
    """DOCSTRING"""

    m = _FILTER.match(filter)

    if not m:
        raise exceptions.InvalidFilter(filter)

    key = m[1]
    op = m[2]
    value = m[3]

    if key not in labels:
        return False

    target_value = labels[key]

    if op == "=":
        return value == target_value

    if op == "!=":
        return value != target_value

    if op == "~=":
        value = re.compile(value)
        return value.match(target_value) is not None

    if op == "~!":
        value = re.compile(value)
        return value.match(target_value) is None

    raise exceptions.InternalError(f"{op}: unknown filter operation")


def _eval_filters(filters: [str], labels: dict[str, str]):
    """DOCSTRING"""

    for filter in filters:
        if not _eval_filter(filter, labels):
            return False

    return True


def _trim(dag: "DAG", components_to_keep: set[Component], links_to_keep: set[Link]):
    """DOCSTRING"""

    components_to_remove = set(dag.components.keys()) - components_to_keep
    links_to_remove = set(dag.links.keys()) - links_to_keep

    for link_name in links_to_remove:
        link = dag.links[link_name]

        source = dag.components[link.source]
        destination = dag.components[link.destination]

        outbound_links = source.outbound_links[destination.name]
        outbound_links.remove(link_name)

        if not outbound_links:
            source.outbound_links.pop(destination.name)

        inbound_links = destination.inbound_links[source.name]
        inbound_links.remove(link_name)

        if not inbound_links:
            destination.inbound_links.pop(source.name)

        dag.links.pop(link_name)

    for component_name in components_to_remove:
        dag.components.pop(component_name)


def _apply_filters(dag: "DAG", filters: [str]) -> "DAG":
    """DOCSTRING"""

    if not filters:
        return dag

    components_to_keep = set()
    links_to_keep = set()

    for component in dag.components.values():
        if _eval_filters(filters, component.labels):
            components_to_keep.add(component.name)

    for link in dag.links.values():
        if _eval_filters(filters, link.labels):
            has_source = link.source in components_to_keep
            has_destination = link.destination in components_to_keep

            if has_source and has_destination:
                links_to_keep.add(link.name)

    _trim(dag, components_to_keep, links_to_keep)

    return dag


def _select_components(dag: "DAG", components: [str]) -> "DAG":
    """DOCSTRING"""

    if not components:
        return dag

    components_to_keep = set()
    links_to_keep = set()

    while len(components) != 0:
        component = components.pop()

        if component not in dag.components:
            raise exceptions.ComponentNotFound(component)

        component = dag.components[component]

        if component.name not in components_to_keep:
            components_to_keep.add(component.name)

            for component_name, inbound_links in component.inbound_links.items():
                components.append(component_name)

                for link in inbound_links:
                    links_to_keep.add(link)

    _trim(dag, components_to_keep, links_to_keep)

    return dag


class DAG:
    """DOCSTRING"""

    def __init__(self, revision: int):
        self.revision = revision
        self.components = {}
        self.links = {}

    def _dfs_check(self,
                   visited_components: set[str],
                   seen_components: set[str],
                   component: str) -> bool:
        """DOCSTRING"""

        if component in seen_components:
            raise exceptions.CycleDetected()

        seen_components.add(component)
        visited_components.add(component)

        for child_component in self.components[component].outbound_links:
            self._dfs_check(visited_components, seen_components, child_component)

        seen_components.remove(component)

    def empty(self) -> bool:
        """DOCSTRING"""

        return not self.components

    def create_component(self,
                         name: str,
                         type: str,
                         parameters: dict[str, str],
                         labels: dict[str, str]) -> Component:
        # pylint: disable=W0622

        """DOCSTRING"""

        if name in self.components:
            raise exceptions.ComponentExists(name)

        component = Component(name, type, parameters, labels)

        self.components[name] = component
        return component

    def get_component(self, name: str) -> Component:
        """DOCSTRING"""

        if name not in self.components:
            raise exceptions.ComponentNotFound(name)

        return self.components[name]

    def remove_component(self, name: str) -> Component:
        """DOCSTRING"""

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
                    parameters: dict[str, str],
                    labels: dict[str, str]) -> Link:
        # pylint: disable=R0913,W0622

        """DOCSTRING"""

        if name in self.links:
            raise exceptions.LinkExists(name)

        if source == destination:
            raise exceptions.CycleDetected()

        if source not in self.components:
            raise exceptions.ComponentNotFound(source)

        if destination not in self.components:
            raise exceptions.ComponentNotFound(destination)

        link = Link(name, type, source, destination, parameters, labels)

        self.components[destination].add_inbound_link(source, name)
        self.components[source].add_outbound_link(destination, name)

        self.links[name] = link
        return link

    def get_link(self, name: str) -> Component:
        """DOCSTRING"""

        if name not in self.links:
            raise exceptions.LinkNotFound(name)

        return self.links[name]

    def remove_link(self, name: str) -> Link:
        """DOCSTRING"""

        link = self.get_link(name)

        self.components[link.destination].remove_inbound_link(link.source, name)
        self.components[link.source].remove_outbound_link(link.destination, name)

        return self.links.pop(name)

    def verify(self) -> bool:
        """DOCSTRING"""

        seen_components = set()
        visited_components = set()

        for root in self.components:
            if root in visited_components:
                continue

            self._dfs_check(visited_components, seen_components, root)

    def filter(self, filters: [str], components: [str]) -> "DAG":
        """DOCSTRING"""

        dag = deepcopy(self)

        dag = _apply_filters(dag, filters)
        dag = _select_components(dag, components)

        return dag

    def dot(self, name: str) -> str:
        """DOCSTRING"""

        graph = pydot.Dot(name, graph_type="digraph")

        for component in self.components.values():
            node = pydot.Node(component.name, label=component.name)
            graph.add_node(node)

        for link in self.links.values():
            edge = pydot.Edge(link.source, link.destination)
            graph.add_edge(edge)

        return graph.to_string()
