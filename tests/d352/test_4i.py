import pytest
import math
import numpy

import FRTB
from tests.utils import get_pair_expected
from tests.trades.ir import IR_SWAP, NON_YIELD_SWAP

_CFG = {
    "sensitivity": FRTB.D352_1["sensitivity"],
}


def test_75():
    # Todo check the calculation
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "xxx 3m", [1, ]))
    result = engine.calculate()

    assert result["total"] == 1 * 2.4


def test_75a_inflation():
    # Note to make the inflation RF work out we need to set the tenor to nan.
    engine = FRTB.init(_CFG)
    engine.add(NON_YIELD_SWAP("XXX", "xxx CPI", 'inflation', 1))
    result = engine.calculate()

    assert result["total"] == 1 * 2.25


def test_75a_basis():
    # Note to make the inflation RF work out we need to set the tenor to nan.
    engine = FRTB.init(_CFG)
    engine.add(NON_YIELD_SWAP("XXX", "xxx basis", 'basis', 1))
    result = engine.calculate()

    assert result["total"] == 1 * 2.25


def test_75c():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("CAD", "CAD 3m", [1, ]))
    result = engine.calculate()

    assert float(result["total"]) == pytest.approx(1 * 2.4 / math.sqrt(2))


def test_76():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "XXX 3m", [1, ]))
    engine.add(IR_SWAP("XXX", "XXX 1d", [3, ]))
    result = engine.calculate()

    expected = get_pair_expected(2.4, 3 * 2.4, 0.999)
    assert float(result["total"]) == pytest.approx(expected)


def test_77():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "XXX 3m", [1, ]))
    engine.add(IR_SWAP("XXX", "XXX 3m", [0, 3, ]))
    result = engine.calculate()

    corr = numpy.exp(-0.03 * (0.25 / 0.25))
    expected = get_pair_expected(1.0 * 2.4, 3.0 * 2.4, corr)
    assert float(result["total"]) == pytest.approx(expected, abs=0.0001)


def test_78():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "XXX 3m", [1, ]))
    engine.add(IR_SWAP("XXX", "XXX 6m", [0, 3, ]))
    result = engine.calculate()

    corr = numpy.exp(-0.03 * (0.25 / 0.25)) * 0.999
    expected = get_pair_expected(1.0 * 2.4, 3.0 * 2.4, corr)
    assert float(result["total"]) == pytest.approx(expected, abs=0.0001)


def test_79():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "XXX 3m", [1, ]))
    engine.add(NON_YIELD_SWAP("XXX", "xxx CPI", 'inflation', 3))
    result = engine.calculate()

    expected = get_pair_expected(1.0 * 2.4, 3.0 * 2.25, 0.4)
    assert float(result["total"]) == pytest.approx(expected, abs=0.0001)


def test_80():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "XXX 3m", [1, ]))
    engine.add(NON_YIELD_SWAP("XXX", "xxx USD", 'basis', 3))
    result = engine.calculate()

    expected = get_pair_expected(1.0 * 2.4, 3.0 * 2.25, 0.0)
    assert float(result["total"]) == pytest.approx(expected, abs=0.0001)


def test_81():
    engine = FRTB.init(_CFG)
    engine.add(IR_SWAP("XXX", "XXX 3m", [1, ]))
    engine.add(IR_SWAP("YYY", "YYY 3m", [3, ]))
    result = engine.calculate()

    expected = get_pair_expected(1.0 * 2.4, 3.0 * 2.4, 0.5)
    assert float(result["total"]) == pytest.approx(expected, abs=0.0001)
