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
from demo import psycopg
from demo import python_app
from demo import python_service
from demo import react_app
from demo import terraform
from demo import volume
from demo import zookeeper


repository = {
    "v1": {
        "components": {
            "demo/python-app": python_app.Component,
            "demo/python-service": python_service.Component,
            "demo/postgres": postgres.Component,
            "demo/zookeeper": zookeeper.Component,
            "demo/kafka": kafka.Component,
            "demo/persistent-volume": persistent_volume.Component,
            "demo/load-balancer": load_balancer.Component,
            "demo/react-app": react_app.Component
        },
        "links": {
            "demo/network": network.Link,
            "demo/psycopg": psycopg.Link,
            "demo/volume": volume.Link,
            "demo/postgres-data": postgres.DataLink,
            "demo/zookeeper-data": zookeeper.DataLink,
            "demo/kafka-data": kafka.DataLink,
            "demo/zookeeper-kafka": kafka.ZookeeperLink,
            "demo/kafka-python": kafka_python.Link,
            "demo/ingress": load_balancer.Link
        },
        "providers": {
            "demo/k8s": k8s.Provider,
            "demo/terraform": terraform.Provider,
            "demo/docker-compose": docker_compose.Provider
        },
        "interfaces": {
            "demo/k8s": {
                "images": k8s.Images,
                "secrets": k8s.Secrets,
                "services": k8s.Services,
                "deployments": k8s.Deployments,
                "persistent-volumes": k8s.PersistentVolumes,
                "load-balancers": k8s.HttpLoadBalancers,
                "ingress-links": k8s.HttpIngressLinks
            },
            "demo/terraform": {
                "persistent-volumes-provider": terraform.PersistentVolumesProvider
            },
            "demo/docker-compose": {
                "images": docker_compose.Images,
                "secrets": docker_compose.Secrets,
                "services": docker_compose.Services,
                "deployments": docker_compose.Deployments,
                "persistent-volumes": docker_compose.PersistentVolumes,
                "persistent-volumes-provider": docker_compose.PersistentVolumesProvider,
                "load-balancers": docker_compose.HttpLoadBalancers,
                "ingress-links": docker_compose.HttpIngressLinks
            }
        }
    }
}
