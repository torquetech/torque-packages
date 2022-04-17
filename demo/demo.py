# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from demo import k8s
from demo import network
from demo import postgres
from demo import psycopg2
from demo import python_service
from demo import python_task


repository = {
    "v1": {
        "components": {
            "demo/python-task": python_task.Task,
            "demo/python-service": python_service.Service,
            "demo/postgres": postgres.Service
        },
        "links": {
            "demo/network": network.Link,
            "demo/psycopg2": psycopg2.Link
        },
        "providers": {
            "demo/k8s": k8s.Provider,
        }
    }
}
