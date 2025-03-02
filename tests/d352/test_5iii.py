import math
import numpy

import FRTB

from tests.trades.fx import FX_OPTION_BARIER
from tests.trades.ir import BERMUDA_SWAPTION_CAD

from tests.utils import get_pair_expected

_CFG = {
    "sensitivity": FRTB.D352_1["sensitivity"],
}


def test_125():
    engine = FRTB.init(_CFG)
    engine.add(BERMUDA_SWAPTION_CAD('GBP', 'GBP 3m', 1.0, 1.0, [], 0, 3))
    engine.add(BERMUDA_SWAPTION_CAD('GBP', 'GBP 3m', 0.5, 2.0, [], 0, 4))
    result = engine.calculate()

    corr_option = numpy.exp(-0.01 * abs(1.0 - 0.5) / min(1.0, 0.5))
    corr_underlying = numpy.exp(-0.01 * abs(1.0 - 2.0) / min(1.0, 2.0))
    corr = corr_option * corr_underlying

    rw = 55 * math.sqrt(60) / math.sqrt(10)

    assert result["total"] == get_pair_expected(3*rw, 4*rw, corr, 0.1)

def test_126_fx():
    engine = FRTB.init(_CFG)
    engine.add(FX_OPTION_BARIER('GBP', 1.0, 0, 25, 0))
    engine.add(FX_OPTION_BARIER('GBP', 0.5, 0, 45, 0))
    result = engine.calculate()

    correlation = math.exp(-0.01 * abs(1.0 - 0.5) / min(1.0, 0.5))
    expected = 110 * math.sqrt(45 ** 2 + 25 ** 2 + 2 * 45 * 25 * correlation)
    assert result["total"] == expected


def test_127_fx():
    engine = FRTB.init(_CFG)
    engine.add(FX_OPTION_BARIER('GBP', 1.0, 0, 25, 0))
    engine.add(FX_OPTION_BARIER('EUR', 1.0, 0, 45, 0))
    result = engine.calculate()

    gbp_expect = 55 * math.sqrt(40) / math.sqrt(10) * 25
    eur_expect = 55 * math.sqrt(40) / math.sqrt(10) * 45
    assert result["total"] == get_pair_expected(gbp_expect, eur_expect, 0.6)
