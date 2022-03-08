# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from collections import namedtuple
from abc import ABC, abstractmethod

from torque import exceptions


RawOptions = dict[str, str]
Options = namedtuple("Options", ["processed", "defaults", "unused"])

Option = namedtuple("Option", ["name", "description", "default_value", "process_fn"])
OptionsSpec = list[Option]


class Component(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: OptionsSpec = []
    configuration: OptionsSpec = []

    @abstractmethod
    def on_build(self):
        """TODO"""


class Link(ABC):
    # pylint: disable=R0903

    """TODO"""

    parameters: OptionsSpec = []
    configuration: OptionsSpec = []

    @abstractmethod
    def on_build(self):
        """TODO"""


def process_options(options_spec: OptionsSpec, raw_options: RawOptions) -> Options:
    """TODO"""

    spec_keys = {i.name for i in options_spec}
    raw_keys = set(raw_options.keys())

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

    return Options(processed, defaults, unused)
