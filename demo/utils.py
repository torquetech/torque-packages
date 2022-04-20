# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import secrets

from torque import v1


def load_file(name: str) -> str:
    """TODO"""

    with open(name, encoding="utf8") as file:
        return file.read().strip()


def module_path() -> str:
    """TODO"""

    return os.path.dirname(__file__)


def generate_password() -> str:
    """TODO"""

    return secrets.token_urlsafe(16)
