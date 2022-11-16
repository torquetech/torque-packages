# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# This file contains k8s yaml files generated from ingress-nginx helm
# repository. For more details, visit https://kubernetes.github.io/ingress-nginx/

"""TODO"""

import jinja2
import yaml

from torque import do
from torque import do_certificates
from torque import do_domains
from torque import k8s
from torque import hlb
from torque import v1


_INGRESS_LB = jinja2.Template("""apiVersion: v1
kind: Namespace
metadata:
  labels:
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/name: ingress-nginx
  name: {{instance}}
---
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: {{instance}}
automountServiceAccountToken: true
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: {{instance}}
data:
  allow-snippet-annotations: 'true'
  use-proxy-protocol: 'true'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
  name: {{instance}}-ingress-nginx
rules:
  - apiGroups:
      - ''
    resources:
      - configmaps
      - endpoints
      - nodes
      - pods
      - secrets
      - namespaces
    verbs:
      - list
      - watch
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    verbs:
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - nodes
    verbs:
      - get
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - events
    verbs:
      - create
      - patch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses/status
    verbs:
      - update
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingressclasses
    verbs:
      - get
      - list
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
  name: {{instance}}-ingress-nginx
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: {{instance}}-ingress-nginx
subjects:
  - kind: ServiceAccount
    name: ingress-nginx
    namespace: {{instance}}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: {{instance}}
rules:
  - apiGroups:
      - ''
    resources:
      - namespaces
    verbs:
      - get
  - apiGroups:
      - ''
    resources:
      - configmaps
      - pods
      - secrets
      - endpoints
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses/status
    verbs:
      - update
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingressclasses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - configmaps
    resourceNames:
      - ingress-controller-leader
    verbs:
      - get
      - update
  - apiGroups:
      - ''
    resources:
      - configmaps
    verbs:
      - create
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    resourceNames:
      - ingress-controller-leader
    verbs:
      - get
      - update
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    verbs:
      - create
  - apiGroups:
      - ''
    resources:
      - events
    verbs:
      - create
      - patch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: {{instance}}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ingress-nginx
subjects:
  - kind: ServiceAccount
    name: ingress-nginx
    namespace: {{instance}}
---
apiVersion: v1
kind: Service
metadata:
  annotations:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: {{instance}}
spec:
  type: LoadBalancer
  ipFamilyPolicy: SingleStack
  ipFamilies:
    - IPv4
  ports:
    - name: https
      port: 443
      protocol: TCP
      targetPort: http
      appProtocol: http
    - name: http
      port: 80
      protocol: TCP
      targetPort: http
      appProtocol: http
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/component: controller
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: {{instance}}
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/instance: {{instance}}
      app.kubernetes.io/component: controller
  replicas: 1
  revisionHistoryLimit: 10
  minReadySeconds: 0
  template:
    metadata:
      labels:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: {{instance}}
        app.kubernetes.io/component: controller
    spec:
      dnsPolicy: ClusterFirst
      containers:
        - name: controller
          image: 'registry.k8s.io/ingress-nginx/controller:v1.3.1@sha256:54f7fe2c6c5a9db9a0ebf1131797109bb7a4d91f56b9b362bde2abd237dd1974'
          imagePullPolicy: IfNotPresent
          lifecycle:
            preStop:
              exec:
                command:
                - /wait-shutdown
          args:
            - /nginx-ingress-controller
            - --publish-service=$(POD_NAMESPACE)/ingress-nginx-controller
            - --election-id=ingress-controller-leader
            - --controller-class={{instance}}/ingress
            - --ingress-class=nginx
            - --configmap=$(POD_NAMESPACE)/ingress-nginx-controller
            - --ingress-class-by-name=true
          securityContext:
            capabilities:
              drop:
              - ALL
              add:
              - NET_BIND_SERVICE
            runAsUser: 101
            allowPrivilegeEscalation: true
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: LD_PRELOAD
              value: /usr/local/lib/libmimalloc.so
          livenessProbe:
            failureThreshold: 5
            httpGet:
              path: /healthz
              port: 10254
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 10254
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          resources:
            requests:
              cpu: 100m
              memory: 90Mi
      nodeSelector:
        kubernetes.io/os: linux
      serviceAccountName: ingress-nginx
      terminationGracePeriodSeconds: 300
---
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: {{instance}}
    app.kubernetes.io/version: '1.3.1'
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/component: controller
  name: {{instance}}-ingress
spec:
  controller: {{instance}}/ingress
""")


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1Implementation(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = hlb.V1ImplementationInterface

    CONFIGURATION = {
        "defaults": {
            "domain": "my-domain.com",
            "certificate_type": "letsencrypt"
        },
        "schema": {
            "domain": str,
            "certificate_type": v1.schema.Or("letsencrypt", "external"),
            v1.schema.Optional("certificate"): {
                "certificate_file": str,
                "key_file": str
            }
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            },
            "k8s": {
                "interface": k8s.V1Provider,
                "required": True
            },
            "domains": {
                "interface": do_domains.V1Provider,
                "required": False
            },
            "certs": {
                "interface": do_certificates.V1Provider,
                "required": True
            }
        }

    def _create_hlb(self,
                    domain: str,
                    certificate_id: v1.utils.Future[str],
                    ingress_list: [hlb.Ingress]):
        """TODO"""

        sanitized_name = self.name.replace(".", "-")
        sanitized_name = sanitized_name.replace("_", "-")

        objs = _INGRESS_LB.render(instance=sanitized_name)

        for obj in objs.split("---"):
            obj = yaml.safe_load(obj)

            if obj["kind"] == "Service":
                hosts = sorted([f"{i.host}.{domain}." for i in ingress_list])
                hosts = ",".join(hosts)

                obj["metadata"]["annotations"] = {
                    "external-dns.alpha.kubernetes.io/hostname": hosts,
                    "service.beta.kubernetes.io/do-loadbalancer-name": sanitized_name,
                    "service.beta.kubernetes.io/do-loadbalancer-protocol": "http",
                    "service.beta.kubernetes.io/do-loadbalancer-tls-ports": "443",
                    "service.beta.kubernetes.io/do-loadbalancer-certificate-id": certificate_id,
                    "service.beta.kubernetes.io/do-loadbalancer-redirect-http-to-https": "true",
                    "service.beta.kubernetes.io/do-loadbalancer-enable-backend-keepalive": "true",
                    "service.beta.kubernetes.io/do-loadbalancer-enable-proxy-protocol": "true"
                }

            self.interfaces.k8s.add_object(obj)

        for ingress in ingress_list:
            ingress_id = ingress.id.replace("_", "-")
            ingress_id = ingress_id.replace(".", "-")

            service, namespace = ingress.service.split(".")

            self.interfaces.k8s.add_object({
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": f"{ingress_id}",
                    "namespace": namespace
                },
                "spec": {
                    "ingressClassName": f"{sanitized_name}-ingress",
                    "rules": [{
                        "host": f"{ingress.host}.{domain}",
                        "http": {
                            "paths": [{
                                "pathType": "Prefix",
                                "path": ingress.path,
                                "backend": {
                                    "service": {
                                        "name": service,
                                        "port": {
                                            "number": ingress.port
                                        }
                                    }
                                }
                            }]
                        }
                    }]
                }
            })

    def create(self, ingress_list: [hlb.Ingress]):
        """TODO"""

        if self.interfaces.domains:
            self.interfaces.domains.create(self.configuration["domain"])

        if self.configuration["certificate_type"] == "external":
            certificate = self.configuration.get("certificate")

            if not certificate:
                raise v1.exceptions.RuntimeError(f"{self.name}: certificate configuration missing")

            certificate_id = self.interfaces.certs.create_external(certificate["certificate_file"],
                                                                   certificate["key_file"])

        else:
            certificate_id = self.interfaces.certs.create_managed(self.configuration["domain"])

        self._create_hlb(self.configuration["domain"], certificate_id, ingress_list)


repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1Implementation
        ]
    }
}
