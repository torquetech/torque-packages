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


def validate_schema(object_type: str,
                    object_definition: object,
                    object_instance: object) -> object:
    """TODO"""

    object_defaults = object_definition["defaults"]
    object_schema = object_definition["schema"]

    object_instance = v1.utils.merge_dicts(object_defaults, object_instance)

    try:
        return schema.Schema(object_schema).validate(object_instance)

    except schema.SchemaError as exc:
        raise RuntimeError(f"{object_type} schema validation failed") from exc


def generate_password() -> str:
    """TODO"""

    return secrets.token_urlsafe(16)
