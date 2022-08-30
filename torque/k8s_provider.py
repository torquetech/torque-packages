# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.bonds.interfaces import k8s as interfaces
from torque.bonds import k8s as bonds
from torque.providers import k8s as providers


repository = {
    "v1": {
        "providers": {
            "torquetech.io/k8s": providers.Provider
        },
        "interfaces": [
            interfaces.KubernetesClient
        ],
        "bonds": {
            "torquetech.io/null-provider": [
                bonds.SimpleKubernetesClient
            ]
        }
    }
}
