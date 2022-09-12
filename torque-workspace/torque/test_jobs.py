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
        self._jobs = jobs
        self._fail_on = fail_on

        self._lock = Lock()
        self._finished = []

    def __iter__(self):
        """TODO"""

        for name, depends in self._jobs.items():
            yield Job(name, depends, self._handler)

    def __len__(self):
        return len(self._jobs)

    def _handler(self, job_name: str):
        """TODO"""

        with self._lock:
            assert job_name not in self._finished

            for depends in self._jobs[job_name]:
                assert depends in self._finished

            self._finished.append(job_name)
            assert job_name not in self._fail_on

    def verify(self) -> bool:
        """TODO"""

        assert sorted(self._finished) == sorted(self._jobs.keys())


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
