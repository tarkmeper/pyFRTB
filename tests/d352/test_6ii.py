import math
import FRTB
from tests.trades.fx import FX_OPTION_BARIER

_CFG = {
    "sensitivity": FRTB.D352_1["sensitivity"],
}


def test_131_fx():
    engine = FRTB.init(_CFG)
    engine.add(FX_OPTION_BARIER('GBP', 1.0, 0, 0, 25))
    result = engine.calculate()

    assert result["total"] == 25
