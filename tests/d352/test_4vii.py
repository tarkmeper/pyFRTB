import math

import FRTB
from tests.trades.fx import *

_CFG = {
    "sensitivity": FRTB.D352_1["sensitivity"],
}


def test_120_specified():
    engine = FRTB.init(_CFG)
    engine.add(FX_CASH_TRADE('GBP', 17))
    result = engine.calculate()

    assert result["total"] == 17 * 21.213  # 17 value * RW


def test_120_general():
    engine = FRTB.init(_CFG)
    engine.add(FX_CASH_TRADE('XXX', 17))
    result = engine.calculate()

    assert result["total"] == 17 * 30  # 17 value * RW


def test_121():
    engine = FRTB.init(_CFG)
    engine.add(FX_CASH_TRADE('GBP', 25))
    engine.add(FX_CASH_TRADE('XXX', 15))
    result = engine.calculate()

    rw_gbp = 25 * 21.213
    rw_xxx = 15 * 30
    expected = math.sqrt(rw_gbp ** 2 + rw_xxx ** 2 + 2 * rw_gbp * rw_xxx * 0.6)
    assert result["total"] == expected  # 17 value * RW
