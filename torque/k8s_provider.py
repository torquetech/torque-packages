# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.bonds.interfaces import k8s as interfaces
from torque.providers import k8s


repository = {
    "v1": {
        "providers": {
            "torquetech.io/k8s": k8s.Provider
        },
        "interfaces": [
            interfaces.KubernetesClient
        ]
    }
}
