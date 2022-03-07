# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import importlib
import pkgutil

__all__ = []

for _, name, _ in pkgutil.walk_packages(__path__):
    m = importlib.import_module(f"{__name__}.{name}")
    __all__.append(name)
