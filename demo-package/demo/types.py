# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple


KeyValue = namedtuple("KeyValue", [
    "key",
    "value"
])

NetworkLink = namedtuple("NetworkLink", [
    "name",
    "object"
])

VolumeLink = namedtuple("VolumeLink", [
    "name",
    "mount_path",
    "object"
])

SecretLink = namedtuple("SecretLink", [
    "name",
    "key",
    "object"
])

Port = namedtuple("Port", [
    "name",
    "protocol",
    "port"
])
