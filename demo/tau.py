# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import tau as tau_v1


class Task(tau_v1.Statement):
    """TODO"""

    def __init__(self,
                 name: str,
                 image: str,
                 network_links: [(str, int)],
                 volume_links: [(str, str)],
                 **kwargs):
        print(image)
        self.name = name
        self.image = image

        self.network_links = network_links
        self.volume_links = volume_links

        if 'replicas' in kwargs:
            self.replicas = kwargs['replicas']

        else:
            self.replicas = 1


class Service(Task):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'port' in kwargs:
            self.port = kwargs['port']

        else:
            self.port = 8080
