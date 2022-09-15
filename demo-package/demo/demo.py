# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from demo import docker_compose
from demo import k8s
from demo import kafka
from demo import kafka_python
from demo import load_balancer
from demo import network
from demo import persistent_volume
from demo import postgres
from demo import providers
from demo import psycopg
from demo import python_app
from demo import python_service
from demo import react_app
from demo import terraform
from demo import volume
from demo import zookeeper


repository = {
    "v1": {
        "components": [
            python_app.Component,
            python_service.Component,
            postgres.Component,
            zookeeper.Component,
            kafka.Component,
            persistent_volume.Component,
            load_balancer.Component,
            react_app.Component
        ],
        "links": [
            network.Link,
            psycopg.Link,
            volume.Link,
            postgres.DataLink,
            zookeeper.DataLink,
            kafka.DataLink,
            kafka.ZookeeperLink,
            kafka_python.Link,
            load_balancer.Link
        ],
        "providers": [
            k8s.Provider,
            terraform.Provider,
            docker_compose.Provider
        ],
        "bonds": [
            k8s.Images,
            k8s.Secrets,
            k8s.Services,
            k8s.Deployments,
            k8s.PersistentVolumes,
            k8s.HttpLoadBalancers,
            k8s.HttpIngressLinks,
            terraform.PersistentVolumesProvider,
            docker_compose.Images,
            docker_compose.Secrets,
            docker_compose.Services,
            docker_compose.Deployments,
            docker_compose.PersistentVolumes,
            docker_compose.PersistentVolumesProvider,
            docker_compose.HttpLoadBalancers,
            docker_compose.HttpIngressLinks,
            docker_compose.Development
        ]
    }
}
