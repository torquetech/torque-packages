# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import kubernetes

from torque import v1


class KubernetesClient(v1.bond.Bond):
    """TODO"""

    def connect(self) -> kubernetes.client.ApiClient:
        """TODO"""

