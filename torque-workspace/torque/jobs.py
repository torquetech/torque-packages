# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os
import threading
import traceback
import typing
import sys

from torque import exceptions
from torque import v1


class Job:
    """DOCSTRING"""

    def __init__(self,
                 name: str,
                 depends: [str],
                 handler: typing.Callable):
        self.name = name
        self.depends = depends
        self.handler = handler

    def __repr__(self) -> str:
        depends = ",".join(self.depends)
        return f"Job({self.name}, depends=[{depends}])"


class _Job:
    """DOCSTRING"""

    def __init__(self,
                 name: str,
                 blocks: [str],
                 depends: int,
                 handler: typing.Callable):
        self.name = name
        self.blocks = blocks
        self.depends = depends
        self.handler = handler


class Runner:
    """DOCSTRING"""

    def __init__(self, worker_count: int):
        self._worker_count = worker_count
        self._workers = []

        self._queue_cond = threading.Condition()
        self._queue = []

        self._jobs_lock = threading.Lock()
        self._jobs = {}

        self._exception = False

    def _pop(self):
        """DOCSTRING"""

        with self._queue_cond:
            while True:
                if len(self._queue) != 0:
                    if self._queue[0] is None:
                        return None

                    return self._queue.pop(0)

                self._queue_cond.wait()

    def _push(self, job):
        """DOCSTRING"""

        with self._queue_cond:
            self._queue.append(job)
            self._queue_cond.notify()

    def _quit(self):
        """DOCSTRING"""

        with self._queue_cond:
            self._queue.append(None)
            self._queue_cond.notify_all()

    def _abort(self):
        """DOCSTRING"""

        with self._queue_cond:
            self._queue.insert(0, None)
            self._queue_cond.notify_all()

    def _worker(self):
        """DOCSTRING"""

        while True:
            job = self._pop()

            if job is None:
                break

            # pylint: disable=W0703
            try:
                job.handler(job.name)

                with self._jobs_lock:
                    for blocked_job in job.blocks:
                        blocked_job = self._jobs[blocked_job]

                        assert blocked_job.depends > 0
                        blocked_job.depends -= 1

                        if blocked_job.depends == 0:
                            self._jobs.pop(blocked_job.name)
                            self._push(blocked_job)

                    if len(self._jobs) == 0:
                        self._quit()

            except v1.exceptions.TorqueException as exc:
                if os.getenv("TORQUE_DEBUG"):
                    traceback.print_exc()

                print(exc, file=sys.stderr)

                self._exception = True
                self._abort()

            except BaseException:
                traceback.print_exc()

                self._exception = True
                self._abort()

    def execute(self, jobs: [Job]):
        """DOCSTRING"""

        self._jobs = {
            job.name: _Job(job.name, [], len(job.depends), job.handler) for job in jobs
        }

        try:
            for job in jobs:
                for dependant in job.depends:
                    dependant = self._jobs[dependant]
                    dependant.blocks.append(job.name)

            for job in list(jobs):
                job = self._jobs[job.name]

                if job.depends == 0:
                    self._jobs.pop(job.name)
                    self._push(job)

            if len(self._jobs) == len(jobs):
                raise exceptions.InternalError("no roots found")

            for _ in range(self._worker_count):
                thr = threading.Thread(target=self._worker)
                thr.start()

                self._workers.append(thr)

        except Exception:
            self._abort()
            raise

        finally:
            for worker in self._workers:
                worker.join()

            self._queue = []
            self._jobs = {}
            self._workers = []

            if self._exception:
                raise exceptions.OperationAborted()


def execute(worker_count: int, jobs: [Job]):
    """DOCSTRING"""

    runner = Runner(worker_count)
    runner.execute(jobs)
