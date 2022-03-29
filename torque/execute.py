# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections.abc import Callable

from torque.model import DAG

from torque.jobs import Job
from torque.jobs import Runner


def _callback_helper(_, data: tuple) -> bool:
    callback, type, args = data
    return callback(type, args)


def from_roots(worker_count: int, dag: DAG, callback: Callable[[object], bool]):
    """TODO"""

    jobs = []

    for component in dag.components:
        depends = [f"link/{link}" for link in dag.components[component].inbound_links.values()]
        data = (callback, "component", component)

        job = Job(f"component/{component}", depends, _callback_helper, data)
        jobs.append(job)

        for _, link in dag.components[component].outbound_links.items():
            depends = [f"component/{component}"]
            data = (callback, "link", link)

            job = Job(f"link/{link}", depends, _callback_helper, data)
            jobs.append(job)

    runner = Runner(worker_count)
    runner.execute(jobs)


def from_leafs(worker_count: int, dag: DAG, callback: Callable[[object], bool]):
    """TODO"""

    jobs = []

    for component in dag.components:
        depends = [f"link/{link}" for link in dag.components[component].outbound_links.values()]
        data = (callback, "component", component)

        job = Job(f"component/{component}", depends, _callback_helper, data)
        jobs.append(job)

        for _, link in dag.components[component].inbound_links.items():
            depends = [f"component/{component}"]
            data = (callback, "link", link)

            job = Job(f"link/{link}", depends, _callback_helper, data)
            jobs.append(job)

    runner = Runner(worker_count)
    runner.execute(jobs)
