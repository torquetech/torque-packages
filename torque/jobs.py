# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from copy import deepcopy
from collections.abc import Callable

from threading import Condition
from threading import Lock
from threading import Thread


class Job:
    """TODO"""

    def __init__(self,
                 name: str,
                 depends: list[str],
                 handler: Callable[[str, object], bool],
                 data: object):
        self.name = name
        self.blocks = []
        self.depends = depends
        self.handler = handler
        self.data = data

    def __repr__(self) -> str:
        depends = ','.join(self.depends)
        return f"Job({self.name}, depends=[{depends}])"


class Runner:
    """TODO"""

    def __init__(self, worker_count: int):
        self.worker_count = worker_count
        self.workers = []

        self.queue_cond = Condition()
        self.queue = []

        self.jobs_lock = Lock()
        self.jobs = {}

    def _pop(self):
        """TODO"""

        with self.queue_cond:
            while True:
                if len(self.queue) != 0:
                    if self.queue[0] is None:
                        return None

                    return self.queue.pop(0)

                self.queue_cond.wait()

    def _push(self, job):
        """TODO"""

        with self.queue_cond:
            self.queue.append(job)
            self.queue_cond.notify()

    def _quit(self):
        """TODO"""

        with self.queue_cond:
            self.queue.append(None)
            self.queue_cond.notify_all()

    def _abort(self):
        """TODO"""

        with self.queue_cond:
            self.queue.insert(0, None)
            self.queue_cond.notify_all()

    def _worker(self):
        """TODO"""

        while True:
            job = self._pop()

            if job is None:
                break

            try:
                if not job.handler(job.name, job.data):
                    self._abort()
                    break

                with self.jobs_lock:
                    for blocked_job in job.blocks:
                        blocked_job = self.jobs[blocked_job]
                        blocked_job.depends.remove(job.name)

                        if len(blocked_job.depends) == 0:
                            self.jobs.pop(blocked_job.name)
                            self._push(blocked_job)

                    if len(self.jobs) == 0:
                        self._quit()

            except Exception:
                self._abort()
                raise

    def execute(self, jobs: list[Job]):
        """TODO"""

        jobs = dict((job.name, Job(job.name, deepcopy(job.depends), job.handler, job.data))
                    for job in jobs)

        try:
            for job in jobs.values():
                for dependant in job.depends:
                    dependant = jobs[dependant]
                    dependant.blocks.append(job.name)

                if len(job.depends) == 0:
                    self._push(job)

                else:
                    self.jobs[job.name] = job

            for _ in range(self.worker_count):
                thr = Thread(target=self._worker)
                thr.start()

                self.workers.append(thr)

        except Exception:
            self._abort()
            raise

        finally:
            for worker in self.workers:
                worker.join()

            self.queue = []
            self.jobs = {}
            self.workers = []


def execute(worker_count: int, jobs: list[Job]):
    """TODO"""

    runner = Runner(worker_count)
    runner.execute(jobs)
