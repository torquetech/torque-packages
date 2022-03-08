# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import exceptions
from torque import types


def test_test1():
    """TODO"""

    options_spec = [
        types.Option("p1", "desc1", "123", int),
        types.Option("p2", "desc2", None, float)
    ]

    raw_options = {
        "p1": "321",
        "p2": "432"
    }

    options = types.process_options(options_spec, raw_options)

    assert len(options.processed) == 2
    assert len(options.defaults) == 0
    assert len(options.unused) == 0
    assert "p1" in options.processed
    assert "p2" in options.processed
    assert options.processed["p1"] == 321
    assert options.processed["p2"] == 432


def test_test2():
    """TODO"""

    options_spec = [
        types.Option("p1", "desc1", "123", int),
        types.Option("p2", "desc2", None, float)
    ]

    raw_options = {
        "p2": "432"
    }

    options = types.process_options(options_spec, raw_options)

    assert len(options.processed) == 2
    assert len(options.defaults) == 1
    assert len(options.unused) == 0
    assert "p1" in options.processed
    assert "p2" in options.processed
    assert options.processed["p1"] == 123
    assert options.processed["p2"] == 432
    assert options.defaults[0] == "p1"


def test_test3():
    """TODO"""

    options_spec = [
        types.Option("p1", "desc1", "123", int),
        types.Option("p2", "desc2", None, float)
    ]

    raw_options = {
    }

    try:
        types.process_options(options_spec, raw_options)
        assert False

    except exceptions.OptionRequired:
        pass


def test_test4():
    """TODO"""

    options_spec = [
        types.Option("p1", "desc1", "123", int),
        types.Option("p2", "desc2", None, float)
    ]

    raw_options = {
        "p1": "321",
        "p2": "432",
        "p3": "674"
    }

    options = types.process_options(options_spec, raw_options)

    assert len(options.processed) == 2
    assert len(options.defaults) == 0
    assert len(options.unused) == 1
    assert "p1" in options.processed
    assert "p2" in options.processed
    assert options.processed["p1"] == 321
    assert options.processed["p2"] == 432
    assert options.unused[0] == "p3"
