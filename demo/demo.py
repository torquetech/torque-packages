# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from demo import configmap
from demo import ebs_volume
from demo import k8s
from demo import network
from demo import pg_data
from demo import postgres
from demo import psycopg
from demo import python_app
from demo import python_service
from demo import terraform
from demo import volume


repository = {
    "v1": {
        "components": {
            "demo/python-app": python_app.Component,
            "demo/python-service": python_service.Component,
            "demo/postgres": postgres.Component,
            "demo/configmap": configmap.Component,
            "demo/ebs-volume": ebs_volume.Component
        },
        "links": {
            "demo/network": network.Link,
            "demo/psycopg": psycopg.Link,
            "demo/volume": volume.Link,
            "demo/pg-data": pg_data.Link,
        },
        "providers": {
            "demo/k8s": k8s.Provider,
            "demo/terraform": terraform.Provider
        },
        "interfaces": {
            "demo/k8s": {
                "images": k8s.Images,
                "secrets": k8s.Secrets,
                "services": k8s.Services,
                "deployments": k8s.Deployments,
                "configmaps": k8s.ConfigMaps,
                "ebs-volumes": k8s.EBSVolumes
            },
            "demo/terraform": {
                "ebs-provider": terraform.EBSProvider
            }
        }
    }
}
