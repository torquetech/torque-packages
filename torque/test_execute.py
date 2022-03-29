# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from threading import Lock

from torque import exceptions
from torque import execute
from torque import model


class JobRunner:
    """TODO"""

    def __init__(self):
        self.lock = Lock()
        self.completed_components = []
        self.completed_links = []

    def on_execute(self, type: str, name: str) -> bool:
        """TODO"""

        with self.lock:
            if type == "component":
                self.completed_components.append(name)

            elif type == "link":
                self.completed_links.append(name)

            else:
                assert False

            return True

    def verify(self, dag: model.DAG):
        """TODO"""

        assert sorted(self.completed_components) == sorted(dag.components)
        assert sorted(self.completed_links) == sorted(dag.links)


def _has_cycles(dag: model.DAG) -> bool:
    """TODO"""

    try:
        dag.verify()
        return False

    except exceptions.CycleDetected:
        pass

    return True


def test_test1():
    """TODO"""

    dag = model.DAG(0)

    dag.create_group("group1")

    dag.create_component("component1", "group1", "component_type", None)
    dag.create_component("component2", "group1", "component_type", None)
    dag.create_component("component3", "group1", "component_type", None)
    dag.create_component("component4", "group1", "component_type", None)
    dag.create_component("component5", "group1", "component_type", None)
    dag.create_component("component6", "group1", "component_type", None)

    dag.create_link("link1", "component1", "component2", "link_type", None)
    dag.create_link("link2", "component2", "component3", "link_type", None)
    dag.create_link("link3", "component2", "component4", "link_type", None)
    dag.create_link("link4", "component3", "component5", "link_type", None)
    dag.create_link("link5", "component4", "component5", "link_type", None)
    dag.create_link("link6", "component5", "component6", "link_type", None)

    assert _has_cycles(dag) is False

    runner = JobRunner()
    execute.from_roots(1, dag, runner.on_execute)

    runner.verify(dag)


def test_test2():
    """TODO"""

    dag = model.DAG(0)

    dag.create_group("group1")

    dag.create_component("component1", "group1", "component_type", None)
    dag.create_component("component2", "group1", "component_type", None)
    dag.create_component("component3", "group1", "component_type", None)
    dag.create_component("component4", "group1", "component_type", None)
    dag.create_component("component5", "group1", "component_type", None)
    dag.create_component("component6", "group1", "component_type", None)

    dag.create_link("link1", "component1", "component2", "link_type", None)
    dag.create_link("link2", "component2", "component3", "link_type", None)
    dag.create_link("link3", "component2", "component4", "link_type", None)
    dag.create_link("link4", "component3", "component5", "link_type", None)
    dag.create_link("link5", "component4", "component5", "link_type", None)
    dag.create_link("link6", "component5", "component6", "link_type", None)

    assert _has_cycles(dag) is False

    runner = JobRunner()
    execute.from_leafs(1, dag, runner.on_execute)

    runner.verify(dag)
