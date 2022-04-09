# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple


Options = dict[str, str]
OptionSpec = namedtuple(
    "OptionSpec",
    [
        "name",
        "description",
        "default_value",
        "validate_fn"
    ]
)
