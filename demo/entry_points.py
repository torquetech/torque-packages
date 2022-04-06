# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from demo.python_task import PythonTask
from demo.python_service import PythonService


entry_points = {
    "v1": {
        "components": {
            "demo/python-task": PythonTask,
            "demo/python-service": PythonService
        },
        # "links": {
        #     "torquetech.dev/dummy1": DummyLink,
        #     "torquetech.dev/dummy2": DummyLink
        # },
        # "protocols": {
        #     "proto1": CustomProtocol,
        #     "proto2": CustomProtocol
        # },
        # "providers": {
        #     "aws-k8s": AWSK8S,
        #     "aws-k8s-ext": AWSK8SExt
        # }
    }
}
