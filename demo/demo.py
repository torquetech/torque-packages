# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from demo import k8s
from demo import network
from demo import postgres
from demo import psycopg
from demo import python_service
from demo import python_task


repository = {
    "v1": {
        "components": {
            "demo/python-task": python_task.Component,
            "demo/python-service": python_service.Component,
            "demo/postgres": postgres.Component
        },
        "links": {
            "demo/network": network.Link,
            "demo/psycopg": psycopg.Link
        },
        "providers": {
            "demo/k8s/images": k8s.ImagesProvider,
            "demo/k8s/secrets": k8s.SecretsProvider,
            "demo/k8s/services": k8s.ServicesProvider,
            "demo/k8s/deployments": k8s.DeploymentsProvider
        }
    }
}
