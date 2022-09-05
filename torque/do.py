# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import v1
from torque import dolib


def _resolve_futures(obj: object) -> object:
    """TODO"""

    if isinstance(obj, dict):
        return {
            k: _resolve_futures(v) for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            _resolve_futures(v) for v in obj
        ]

    if isinstance(obj, v1.utils.Future):
        return _resolve_futures(obj.get())

    if callable(obj):
        return _resolve_futures(obj())

    return obj


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {},
        "schema": {}
    }

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_apply(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_delete(self, context: v1.deployment.Context, dry_run: bool):
        """TODO"""

    def on_command(self, context: v1.deployment.Context, argv: [str]):
        """TODO"""


repository = {
    "v1": {
        "interfaces": [],
        "providers": {
            "torquetech.io/do": Provider
        }
    }
}
