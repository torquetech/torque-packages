# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple

from torque import exceptions

from torque.v1 import options


RawOptions = dict[str, str]
Options = namedtuple("Options", ["processed", "defaults", "unused", "raw"])


def process(options_spec: options.OptionsSpec, raw_options: RawOptions) -> Options:
    """TODO"""

    spec_keys = {i.name for i in options_spec}
    raw_keys = set(raw_options.keys())

    raw = raw_options
    unused = list(raw_keys - spec_keys)
    defaults = list(spec_keys - raw_keys)

    processed = {}

    for option_spec in options_spec:
        name = option_spec.name
        value = option_spec.default_value

        if name in raw_options:
            value = raw_options[name]

        else:
            if not value:
                raise exceptions.OptionRequired(name)

        if option_spec.process_fn:
            value = option_spec.process_fn(value)

        processed[name] = value

    return Options(processed, defaults, unused, raw)
