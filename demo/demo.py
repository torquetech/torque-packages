# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from demo import python_task
from demo import python_service
from demo import providers


repository = {
    "v1": {
        "components": {
            "demo/python-task": python_task.Task,
            "demo/python-service": python_service.Service
        },
        # "links": {
        #     "torquetech.dev/dummy1": DummyLink,
        #     "torquetech.dev/dummy2": DummyLink
        # },
        # "protocols": {
        #     "proto1": CustomProtocol,
        #     "proto2": CustomProtocol
        # },
        "providers": {
            "demo/aws-k8s": providers.AWSK8S,
        }
    }
}
