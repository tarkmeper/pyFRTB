import pytest
from copy import deepcopy
import FRTB

from tests.trades.bond import CREDIT_BOND_1
from tests.trades.equity import CASH_DEF

_CFG = {
    "jtd": FRTB.D352_1["jtd"],
}


def _create_trade(base, value, seniority, sector, name, rating, tenor, subproduct=None):
    val = deepcopy(base)
    val.update({
        "maturity": tenor,
        "jtd": [{
            "sector": sector,
            "seniority": seniority,
            "name": name,
            "rating": rating,
            "value": value,
        }]
    })
    if subproduct:
        val["level2-product"] = subproduct
    return val


def test_137():
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, 500, "senior", "financial", "TestName4", "AAA", 1.0),
    trade2 = _create_trade(CREDIT_BOND_1, 1000, "senior", "financial", "ABC", "AAA", 1.0)
    engine.add(trade1)
    engine.add(trade2)
    result = engine.calculate()
    assert result["total"] == 3.75


def test_139():
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, 500, "subordinate0", "technology", "Apple", "AAA", 1.0)
    trade2 = _create_trade(CREDIT_BOND_1, -1000, "equity", "technology", "Apple", "AAA", 1.0)
    engine.add(trade1)
    engine.add(trade2)
    result = engine.calculate()

    assert result["total"] == 0.0


def test_139_rev():
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, -500, "subordinate0", "technology", "Apple", "AAA", 1.0)
    trade2 = _create_trade(CREDIT_BOND_1, 1000, "equity", "technology", "Apple", "AAA", 1.0)
    engine.add(trade1)
    engine.add(trade2)
    result = engine.calculate()

    assert float(result["total"]) == pytest.approx(3.3333, 0.0001)


def test_144():
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, 1000, "super-senior", "technology", "ABCD", "AAA", 1.0, subproduct="covered")
    engine.add(trade1)
    result = engine.calculate()

    expected = 1000 * 0.25 * 0.005  # Notional * Covered LGD * RW
    assert result["total"] == expected


def test_146_long():
    """ Maturity more than a year is capped at 1yr (1.0 factor)"""
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, 1000, "senior", "financial", "TestName4", "AAA", 500)
    engine.add(trade1)
    result = engine.calculate()
    assert result["total"] == 1000 * 0.75 * 0.005 * 1.0  # Notional * LGD * RW  * Maturity


def test_146_mid():
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, 1000, "senior", "financial", "TestName4", "AAA", 1.0 / 3)
    engine.add(trade1)
    result = engine.calculate()
    assert result["total"] == 1000 * 0.75 * 0.005 / 3.0  # Notional * LGD * RW / maturity


def test_149():
    engine = FRTB.init(_CFG)
    trade1 = _create_trade(CREDIT_BOND_1, 1000, "senior", "financial", "TestName4", "AAA", 1.0 / 5)
    engine.add(trade1)
    result = engine.calculate()
    assert result["total"] == 1000 * 0.75 * 0.005 / 4.0  # Notional * LGD * RW / maturity [ capped at 0.25 ]


def test_155():
    engine = FRTB.init(_CFG)
    engine.add(_create_trade(CREDIT_BOND_1, 2000, "super-senior", "financial", "ABC", "AAA", 1.0))
    engine.add(_create_trade(CREDIT_BOND_1, 1000, "senior", "financial", "ABC", "AAA", 1.0))
    engine.add(_create_trade(CASH_DEF, -500, "equity", "financial", "ABC", "AAA", 1.0))
    result = engine.calculate()

    target = (3000 * 0.75 - 500 * 0.25) * 0.005  # rember equity maturity
    assert result["total"] == target


def test_155_senior_shorts():
    engine = FRTB.init(_CFG)
    engine.add(_create_trade(CREDIT_BOND_1, -2000, "super-senior", "financial", "ABC", "AAA", 1.0))
    engine.add(_create_trade(CREDIT_BOND_1, -1000, "senior", "financial", "ABC", "AAA", 1.0))
    engine.add(_create_trade(CASH_DEF, 500, "equity", "financial", "ABC", "AAA", 1.0))
    result = engine.calculate()

    assert float(result["total"]) == pytest.approx(0.03289473684210531)


def test_156_different_buckets():
    engine = FRTB.init(_CFG)
    engine.add(_create_trade(CREDIT_BOND_1, -2000, "super-senior", "sovereign", "ABC", "AAA", 1.0))
    engine.add(_create_trade(CREDIT_BOND_1, -1000, "senior", "sovereign", "ABC", "AAA", 1.0))
    engine.add(_create_trade(CASH_DEF, 500, "equity", "financial", "ABC", "AAA", 1.0))
    result = engine.calculate()

    expected = 500 * 0.25 * 0.005  # notional * maturity * RW
    assert float(result["total"]) == 0.625
