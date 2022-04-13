# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque.v1 import provider


class Deployment:
    """TODO"""

    def __init__(self, name: str, profile: str, dry_run: bool, providers: [provider.Provider]):
        self.name = name
        self.profile = profile
        self.dry_run = dry_run
        self._providers = providers


def create(name: str, profile: str, dry_run: bool, providers: [provider.Provider]) -> Deployment:
    """TODO"""

    return Deployment(name, profile, dry_run, providers)
