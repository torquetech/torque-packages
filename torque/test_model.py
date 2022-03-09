# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import exceptions
from torque import model


class Component(model.ComponentType):
    """TODO"""


class Link(model.LinkType):
    """TODO"""


_modules = {
    "components.v1": {
        "component_type", Component
    },
    "links.v1": {
        "link_type", Link
    }
}


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

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")
    dag.create_cluster("cluster2")
    dag.create_cluster("cluster3")

    dag.create_component("component1", "cluster1", "component_type", {})
    dag.create_component("component2", "cluster1", "component_type", {})
    dag.create_component("component3", "cluster1", "component_type", {})
    dag.create_component("component4", "cluster1", "component_type", {})

    dag.create_link("link1", "component1", "component2", "link_type", {})
    dag.create_link("link2", "component1", "component3", "link_type", {})
    dag.create_link("link3", "component2", "component3", "link_type", {})
    dag.create_link("link4", "component3", "component4", "link_type", {})

    assert _has_cycles(dag) is False

    dag.create_link("link5", "component4", "component2", "link_type", {})

    assert _has_cycles(dag) is True

    dag.create_link("link6", "component4", "component1", "link_type", {})

    assert _has_cycles(dag) is True


def test_test2():
    """TODO"""

    dag = model.DAG(0, _modules)

    try:
        dag.create_cluster("cluster1")
        dag.create_cluster("cluster1")

        assert False

    except exceptions.ClusterExists:
        pass


def test_test3():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    try:
        dag.create_component("component1", "cluster1", "component_type", {})
        dag.create_component("component1", "cluster1", "component_type", {})

        assert False

    except exceptions.ComponentExists:
        pass


def test_test4():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})
    dag.create_component("component2", "cluster1", "component_type", {})

    try:
        dag.create_link("link1", "component1", "component2", "link_type", {})
        dag.create_link("link1", "component1", "component2", "link_type", {})

        assert False

    except exceptions.LinkExists:
        pass


def test_test5():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})
    dag.create_component("component2", "cluster1", "component_type", {})

    try:
        dag.create_component("component4", "cluster2", "component_type", {})

        assert False

    except exceptions.ClusterNotFound:
        pass


def test_test6():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})

    try:
        dag.create_link("link1", "_component", "component1", "link_type", {})

        assert False

    except exceptions.ComponentNotFound:
        pass


def test_test7():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})

    try:
        dag.create_link("link1", "component1", "_component", "link_type", {})

        assert False

    except exceptions.ComponentNotFound:
        pass


def test_test8():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})

    try:
        dag.create_link("link1", "component1", "component1", "link_type", {})

        assert False

    except exceptions.CycleDetected:
        pass


def test_test9():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})
    dag.create_component("component2", "cluster1", "component_type", {})

    try:
        dag.create_link("link1", "component1", "component2", "link_type", {})
        dag.create_link("link2", "component1", "component2", "link_type", {})

        assert False

    except exceptions.ComponentsAlreadyConnected:
        pass


def test_test10():
    """TODO"""

    dag = model.DAG(0, _modules)

    assert not _has_cycles(dag)


def test_test11():
    """TODO"""

    dag = model.DAG(0, _modules)

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type", {})
    dag.create_component("component2", "cluster1", "component_type", {})
    dag.create_component("component3", "cluster1", "component_type", {})

    dag.create_link("link1", "component1", "component2", "link_type", {})
    dag.create_link("link2", "component2", "component1", "link_type", {})

    assert _has_cycles(dag)
