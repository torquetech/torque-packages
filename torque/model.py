# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import exceptions
from torque import options


class Group:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Group({self.name})"


class Component:
    """TODO"""

    def __init__(self,
                 name: str,
                 group: str,
                 type: str,
                 params: options.Options):
        # pylint: disable=W0622

        self.name = name
        self.group = group
        self.type = type
        self.params = params

        self.inbound_links: dict[str, str] = {}
        self.outbound_links: dict[str, str] = {}

    def __repr__(self) -> str:
        inbound_links = ",".join(self.inbound_links)
        outbound_links = ",".join(self.outbound_links)

        return f"Component({self.name}" \
               f", group={self.group}" \
               f", inbound_links=[{inbound_links}]" \
               f", outbound_links=[{outbound_links}]" \
               f", type={self.type})"

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


class Link:
    # pylint: disable=R0903

    """TODO"""

    def __init__(self,
                 name: str,
                 source: str,
                 destination: str,
                 type: str,
                 params: options.Options):
        # pylint: disable=R0913,W0622

        self.name = name
        self.source = source
        self.destination = destination
        self.type = type
        self.params = params

    def __repr__(self) -> str:
        return f"Link({self.name}" \
               f", source={self.source}" \
               f", destination={self.destination}" \
               f", type={self.type})"


class DAG:
    """TODO"""

    def __init__(self, revision: int):
        self.revision = revision
        self.groups = {}
        self.components = {}
        self.links = {}

    def create_group(self, name: str) -> Group:
        """TODO"""

        if name in self.groups:
            raise exceptions.GroupExists(name)

        group = Group(name)

        self.groups[name] = group
        return group

    def remove_group(self, name: str) -> Group:
        """TODO"""

        if name not in self.groups:
            raise exceptions.GroupNotFound(name)

        groups_in_use = {i.group for i in self.components.values()}

        if name in groups_in_use:
            raise exceptions.GroupNotEmpty(name)

        return self.groups.pop(name)

    def create_component(self,
                         name: str,
                         group: str,
                         type: str,
                         params: options.Options) -> Component:
        # pylint: disable=W0622

        """TODO"""

        if name in self.components:
            raise exceptions.ComponentExists(name)

        if group not in self.groups:
            raise exceptions.GroupNotFound(group)

        component = Component(name, group, type, params)

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
                    type: str,
                    params: options.Options) -> Link:
        # pylint: disable=R0913,W0622

        """TODO"""

        if name in self.links:
            raise exceptions.LinkExists(name)

        if source == destination:
            raise exceptions.CycleDetected(name)

        if source not in self.components:
            raise exceptions.ComponentNotFound(source)

        if destination not in self.components:
            raise exceptions.ComponentNotFound(destination)

        link = Link(name, source, destination, type, params)

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

        return {i.type for i in self.components.values()}

    def used_link_types(self) -> set[str]:
        """TODO"""

        return {i.type for i in self.links.values()}

    def has_group(self, name: str) -> bool:
        """TODO"""

        return name in self.groups
