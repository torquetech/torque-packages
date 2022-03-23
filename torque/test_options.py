# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

from torque import exceptions
from torque import options

from torque.v1 import interfaces


def test_test1():
    """TODO"""

    spec = [
        interfaces.OptionSpec("p1", "desc1", "123", int),
        interfaces.OptionSpec("p2", "desc2", None, float)
    ]

    raw = {
        "p1": "321",
        "p2": "432"
    }

    opt = options.process(spec, raw)

    assert len(opt.processed) == 2
    assert len(opt.defaults) == 0
    assert len(opt.unused) == 0
    assert "p1" in opt.processed
    assert "p2" in opt.processed
    assert opt.processed["p1"] == 321
    assert opt.processed["p2"] == 432


def test_test2():
    """TODO"""

    spec = [
        interfaces.OptionSpec("p1", "desc1", "123", int),
        interfaces.OptionSpec("p2", "desc2", None, float)
    ]

    raw = {
        "p2": "432"
    }

    opt = options.process(spec, raw)

    assert len(opt.processed) == 2
    assert len(opt.defaults) == 1
    assert len(opt.unused) == 0
    assert "p1" in opt.processed
    assert "p2" in opt.processed
    assert opt.processed["p1"] == 123
    assert opt.processed["p2"] == 432
    assert opt.defaults[0] == "p1"


def test_test3():
    """TODO"""

    spec = [
        interfaces.OptionSpec("p1", "desc1", "123", int),
        interfaces.OptionSpec("p2", "desc2", None, float)
    ]

    raw = {
    }

    try:
        options.process(spec, raw)
        assert False

    except exceptions.OptionRequired:
        pass


def test_test4():
    """TODO"""

    spec = [
        interfaces.OptionSpec("p1", "desc1", "123", int),
        interfaces.OptionSpec("p2", "desc2", None, float)
    ]

    raw = {
        "p1": "321",
        "p2": "432",
        "p3": "674"
    }

    opt = options.process(spec, raw)

    assert len(opt.processed) == 2
    assert len(opt.defaults) == 0
    assert len(opt.unused) == 1
    assert "p1" in opt.processed
    assert "p2" in opt.processed
    assert opt.processed["p1"] == 321
    assert opt.processed["p2"] == 432
    assert opt.unused[0] == "p3"
