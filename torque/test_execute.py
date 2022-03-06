# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from threading import Lock

from torque.model import DAG

from torque.execute import execute_from_roots
from torque.execute import execute_from_leafs


class JobRunner:
    """TODO"""

    def __init__(self):
        self.lock = Lock()
        self.completed_components = []
        self.completed_links = []

    def on_component(self, component: str) -> bool:
        """TODO"""

        with self.lock:
            self.completed_components.append(component)
            return True

    def on_link(self, source: str, destination: str, link: str) -> bool:
        # pylint: disable=W0613

        """TODO"""

        with self.lock:
            self.completed_links.append(link)
            return True

    def verify(self, dag: DAG):
        """TODO"""

        assert sorted(self.completed_components) == sorted(dag.components)
        assert sorted(self.completed_links) == sorted(dag.links)


def test_test1():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component")
    dag.create_component("component2", "cluster1", "component_type")
    dag.create_component("component3", "cluster1", "component_type")
    dag.create_component("component4", "cluster1", "component_type")
    dag.create_component("component5", "cluster1", "component_type")
    dag.create_component("component6", "cluster1", "component_type")

    dag.create_link("link1", "component1", "component2", "link_type")
    dag.create_link("link2", "component2", "component3", "link_type")
    dag.create_link("link3", "component2", "component4", "link_type")
    dag.create_link("link4", "component3", "component5", "link_type")
    dag.create_link("link5", "component4", "component5", "link_type")
    dag.create_link("link6", "component5", "component6", "link_type")

    assert dag.has_cycles() is False

    runner = JobRunner()
    execute_from_roots(1, dag, runner.on_component, runner.on_link)

    runner.verify(dag)


def test_test2():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")
    dag.create_component("component2", "cluster1", "component_type")
    dag.create_component("component3", "cluster1", "component_type")
    dag.create_component("component4", "cluster1", "component_type")
    dag.create_component("component5", "cluster1", "component_type")
    dag.create_component("component6", "cluster1", "component_type")

    dag.create_link("link1", "component1", "component2", "link_type")
    dag.create_link("link2", "component2", "component3", "link_type")
    dag.create_link("link3", "component2", "component4", "link_type")
    dag.create_link("link4", "component3", "component5", "link_type")
    dag.create_link("link5", "component4", "component5", "link_type")
    dag.create_link("link6", "component5", "component6", "link_type")

    assert dag.has_cycles() is False

    runner = JobRunner()
    execute_from_leafs(1, dag, runner.on_component, runner.on_link)

    runner.verify(dag)
