# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.bonds import k8s_config as bonds
from torque.providers import k8s_config


repository = {
    "v1": {
        "providers": {
            "torquetech.io/k8s-config": k8s_config.Provider
        },
        "bonds": {
            "torquetech.io/k8s-config": [
                bonds.KubernetesClient
            ]
        }
    }
}
