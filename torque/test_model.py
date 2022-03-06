# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.model import DAG

from torque.exceptions import DuplicateCluster
from torque.exceptions import DuplicateComponent
from torque.exceptions import DuplicateLink
from torque.exceptions import ClusterNotFound
from torque.exceptions import CycleDetected
from torque.exceptions import ComponentNotFound
from torque.exceptions import LinkAlreadyExists


def test_test1():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")
    dag.create_cluster("cluster2")
    dag.create_cluster("cluster3")

    dag.create_component("component1", "cluster1", "component_type")
    dag.create_component("component2", "cluster1", "component_type")
    dag.create_component("component3", "cluster1", "component_type")
    dag.create_component("component4", "cluster1", "component_type")

    dag.create_link("link1", "component1", "component2", "link_type")
    dag.create_link("link2", "component1", "component3", "link_type")
    dag.create_link("link3", "component2", "component3", "link_type")
    dag.create_link("link4", "component3", "component4", "link_type")

    assert dag.has_cycles() is False

    dag.create_link("link5", "component4", "component2", "link_type")

    assert dag.has_cycles() is True

    dag.create_link("link6", "component4", "component1", "link_type")

    assert dag.has_cycles() is True


def test_test2():
    """TODO"""

    dag = DAG()

    try:
        dag.create_cluster("cluster1")
        dag.create_cluster("cluster1")

        assert False

    except DuplicateCluster:
        pass


def test_test3():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    try:
        dag.create_component("component1", "cluster1", "component_type")
        dag.create_component("component1", "cluster1", "component_type")

        assert False

    except DuplicateComponent:
        pass


def test_test4():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")
    dag.create_component("component2", "cluster1", "component_type")

    try:
        dag.create_link("link1", "component1", "component2", "link_type")
        dag.create_link("link1", "component1", "component2", "link_type")

        assert False

    except DuplicateLink:
        pass


def test_test5():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")
    dag.create_component("component2", "cluster1", "component_type")

    try:
        dag.create_component("component4", "cluster2", "component_type")

        assert False

    except ClusterNotFound:
        pass


def test_test6():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")

    try:
        dag.create_link("link1", "_component", "component1", "link_type")

        assert False

    except ComponentNotFound:
        pass


def test_test7():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")

    try:
        dag.create_link("link1", "component1", "_component", "link_type")

        assert False

    except ComponentNotFound:
        pass


def test_test8():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")

    try:
        dag.create_link("link1", "component1", "component1", "link_type")

        assert False

    except CycleDetected:
        pass


def test_test9():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")
    dag.create_component("component2", "cluster1", "component_type")

    try:
        dag.create_link("link1", "component1", "component2", "link_type")
        dag.create_link("link2", "component1", "component2", "link_type")

        assert False

    except LinkAlreadyExists:
        pass


def test_test10():
    """TODO"""

    dag = DAG()

    assert not dag.has_cycles()


def test_test11():
    """TODO"""

    dag = DAG()

    dag.create_cluster("cluster1")

    dag.create_component("component1", "cluster1", "component_type")
    dag.create_component("component2", "cluster1", "component_type")
    dag.create_component("component3", "cluster1", "component_type")

    dag.create_link("link1", "component1", "component2", "link_type")
    dag.create_link("link2", "component2", "component1", "link_type")

    assert dag.has_cycles()
