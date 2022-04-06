# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import tao as tao_v1


class Task(tao_v1.Statement):
    """TODO"""

    def __init__(self, name: str, image: str, links: [(str, int)], **kwargs):
        print(image)
        self.name = name
        self.image = image
        self.links = links

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
