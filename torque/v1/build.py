# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


class Build:
    """TODO"""

    def __init__(self, deployment: str, profile: str):
        self.deployment = deployment
        self.profile = profile


def create(deployment: str, profile: str) -> Build:
    """TODO"""

    return Build(deployment, profile)
