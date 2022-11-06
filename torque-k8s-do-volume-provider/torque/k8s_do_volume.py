# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import do
from torque import k8s
from torque import v1


class V1Provider(v1.provider.Provider):
    """TODO"""


class V1Implementation(v1.bond.Bond):
    """TODO"""

    PROVIDER = V1Provider
    IMPLEMENTS = k8s.V1VolumeInterface

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
            }
        }

    def create(self, name: str, size: str) -> dict[str, object]:
        """TODO"""

        self.interfaces.k8s.add_object({
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": name,
                "namespace": self.interfaces.k8s.namespace()
            },
            "spec": {
                "accessModes": [
                    "ReadWriteOnce"
                ],
                "resources": {
                    "requests": {
                        "storage": size
                    }
                },
                "storageClassName": "do-block-storage"
            }
        })

        return {
            "name": name,
            "persistentVolumeClaim": {
                "claimName": name
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
