# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import exceptions
from torque import model


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

    dag.create_component("component1", "component_type", None)
    dag.create_component("component2", "component_type", None)
    dag.create_component("component3", "component_type", None)
    dag.create_component("component4", "component_type", None)

    dag.create_link("link1", "link_type", "component1", "component2", None)
    dag.create_link("link2", "link_type", "component1", "component3", None)
    dag.create_link("link3", "link_type", "component2", "component3", None)
    dag.create_link("link4", "link_type", "component3", "component4", None)

    assert _has_cycles(dag) is False

    dag.create_link("link5", "link_type", "component4", "component2", None)

    assert _has_cycles(dag) is True

    dag.create_link("link6", "link_type", "component4", "component1", None)

    assert _has_cycles(dag) is True


def test_test2():
    """TODO"""

    dag = model.DAG(0)

    try:
        dag.create_component("component1", "component_type", None)
        dag.create_component("component1", "component_type", None)

        assert False

    except exceptions.ComponentExists:
        pass


def test_test3():
    """TODO"""

    dag = model.DAG(0)

    dag.create_component("component1", "component_type", None)
    dag.create_component("component2", "component_type", None)

    try:
        dag.create_link("link1", "link_type", "component1", "component2", None)
        dag.create_link("link1", "link_type", "component1", "component2", None)

        assert False

    except exceptions.LinkExists:
        pass


def test_test4():
    """TODO"""

    dag = model.DAG(0)

    dag.create_component("component1", "component_type", None)

    try:
        dag.create_link("link1", "link_type", "_component", "component1", None)

        assert False

    except exceptions.ComponentNotFound:
        pass


def test_test5():
    """TODO"""

    dag = model.DAG(0)

    dag.create_component("component1", "component_type", None)

    try:
        dag.create_link("link1", "link_type", "component1", "_component", None)

        assert False

    except exceptions.ComponentNotFound:
        pass


def test_test6():
    """TODO"""

    dag = model.DAG(0)

    dag.create_component("component1", "component_type", None)

    try:
        dag.create_link("link1", "link_type", "component1", "component1", None)

        assert False

    except exceptions.CycleDetected:
        pass


def test_test7():
    """TODO"""

    dag = model.DAG(0)

    assert not _has_cycles(dag)


def test_test8():
    """TODO"""

    dag = model.DAG(0)

    dag.create_component("component1", "component_type", None)
    dag.create_component("component2", "component_type", None)
    dag.create_component("component3", "component_type", None)

    dag.create_link("link1", "link_type", "component1", "component2", None)
    dag.create_link("link2", "link_type", "component2", "component1", None)

    assert _has_cycles(dag)
