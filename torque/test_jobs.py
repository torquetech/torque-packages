# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from threading import Lock

from torque.jobs import Job
from torque.jobs import Runner


class Checker:
    """TODO"""

    def __init__(self, jobs: [Job], fail_on: [str]):
        self.jobs = jobs
        self.fail_on = fail_on

        self.lock = Lock()
        self.finished = []

    def __iter__(self):
        """TODO"""

        for name, depends in self.jobs.items():
            yield Job(name, depends, self._handler)

    def _handler(self, job_name: str):
        """TODO"""

        with self.lock:
            assert job_name not in self.finished

            for depends in self.jobs[job_name]:
                assert depends in self.finished

            self.finished.append(job_name)
            return job_name not in self.fail_on

    def verify(self) -> bool:
        """TODO"""

        assert sorted(self.finished) == sorted(self.jobs.keys())


def test_test1():
    """TODO"""

    defs = {
        "job1": ["job2"],
        "job2": ["job3", "job4"],
        "job3": ["job5"],
        "job4": ["job5"],
        "job5": ["job6"],
        "job6": []
    }

    checker = Checker(defs, [])

    runner = Runner(4)
    runner.execute(checker)

    checker.verify()
