# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.model import DAG

from torque.jobs import Job
from torque.jobs import Runner


def _component_helper(_, data: tuple) -> bool:
    (callback, component) = data
    return callback(component)


def _link_helper(_, data: tuple) -> bool:
    (callback, source, destination, link) = data
    return callback(source, destination, link)


def from_roots(worker_count: int, dag: DAG, component_callback, link_callback):
    """TODO"""

    jobs = []

    for component in dag.components:
        depends = [f"link/{link}" for link in dag.components[component].inbound_links.values()]
        data = [component_callback, component]

        job = Job(f"component/{component}", depends, _component_helper, data)
        jobs.append(job)

        for destination, link in dag.components[component].outbound_links.items():
            depends = [f"component/{component}"]
            data = [link_callback, component, destination, link]

            job = Job(f"link/{link}", depends, _link_helper, data)
            jobs.append(job)

    runner = Runner(worker_count)
    runner.execute(jobs)


def from_leafs(worker_count: int, dag: DAG, component_callback, link_callback):
    """TODO"""

    jobs = []

    for component in dag.components:
        depends = [f"link/{link}" for link in dag.components[component].outbound_links.values()]
        data = [component_callback, component]

        job = Job(f"component/{component}", depends, _component_helper, data)
        jobs.append(job)

        for source, link in dag.components[component].inbound_links.items():
            depends = [f"component/{component}"]
            data = [link_callback, source, component, link]

            job = Job(f"link/{link}", depends, _link_helper, data)
            jobs.append(job)

    runner = Runner(worker_count)
    runner.execute(jobs)
