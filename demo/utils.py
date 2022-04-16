# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import secrets

import schema

from torque import v1


def load_file(name: str) -> str:
    """TODO"""

    with open(name, encoding="utf8") as file:
        return file.read().strip()


def module_path() -> str:
    """TODO"""

    return os.path.dirname(__file__)


def validate_schema(type: str, obj: object, obj_defaults: object, obj_schema: schema.Schema) -> object:
    """TODO"""

    obj = v1.utils.merge_dicts(obj_defaults, obj)

    try:
        return obj_schema.validate(obj)

    except schema.SchemaError as exc:
        raise RuntimeError(f"{type} schema validation failed") from exc


def generate_password() -> str:
    """TODO"""

    return secrets.token_urlsafe(16)
