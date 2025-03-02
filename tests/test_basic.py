import copy
import FRTB

from tests.trades.fx import FX_CASH_TRADE
from tests.trades.bond import CREDIT_BOND_1

def test_basic():
    """
    Test that scaling is correctly calculating all the components in a simple test case.
    """
    engine = FRTB.init(FRTB.D352_1)
    engine.add(FX_CASH_TRADE("USD", 0))
    val = engine.calculate()

    # check results match what we expect.
    assert val["total"] == 0.0


def test_scale():
    """
    Test that scaling is correctly calculating all the components in a simple test case.
    """
    engine = FRTB.init(FRTB.D352_1)
    engine.add(FX_CASH_TRADE("USD", 5))
    engine.add(CREDIT_BOND_1)
    val = engine.calculate()

    engine.scale(2.0)
    val2 = engine.calculate()

    # check results match what we expect.
    assert val["total"] * 2 == val2["total"]

def test_merge_and_scaling():
    """
    Test that merging an egine with itself is the same as scaling up by 2
    """
    engine = FRTB.init(FRTB.D352_1)
    engine.add(FX_CASH_TRADE("USD", 5))
    engine.add(CREDIT_BOND_1)
    base_val = engine.calculate()

    # Create a copy of the engine and then double
    engine_clone = copy.deepcopy(engine)
    engine_clone.merge(engine)
    val = engine_clone.calculate()

    engine.scale(2.0)
    val2 = engine.calculate()

    # check results match what we expect.
    assert base_val["total"] * 2 == val2["total"]
    assert val["total"] == val2["total"]


def test_merge_removal():
    """
    Test that merging an object with itself and a wieght of -1 removes it completely.
    """
    engine = FRTB.init(FRTB.D352_1)
    engine.add(FX_CASH_TRADE("USD", 5))
    engine.add(CREDIT_BOND_1)

    json1 = engine.json_dump()

    # Create a copy of the engine and then double
    engine_clone = copy.deepcopy(engine)
    engine_clone.merge(engine, -1)
    val = engine_clone.calculate()

    json2 = engine_clone.json_dump()

    assert val["total"] == 0.0