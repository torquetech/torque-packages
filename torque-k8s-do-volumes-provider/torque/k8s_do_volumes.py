# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

from torque import do
from torque import k8s
from torque import k8s_volumes
from torque import v1


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""


class V1Implementation(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = k8s_volumes.V1Interface

    CONFIGURATION = {
        "defaults": {
            "size": "1G"
        },
        "schema": {
            "size": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            },
            "k8s": {
                "interface": k8s.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with self.interfaces.k8s as p:
            p.add_hook("apply-objects", self._apply)

    def _apply(self) -> dict[str, object]:
        """DOCSTRING"""

        self.interfaces.k8s.add_object({
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": self.name,
                "namespace": self.interfaces.k8s.namespace()
            },
            "spec": {
                "accessModes": [
                    "ReadWriteOnce"
                ],
                "resources": {
                    "requests": {
                        "storage": self.configuration["size"]
                    }
                },
                "storageClassName": "do-block-storage"
            }
        })

    def ref_name(self) -> str:
        """DOCSTRING"""

        return self.name

    def spec(self) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "name": self.name,
            "persistentVolumeClaim": {
                "claimName": self.name
            }
        }


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
