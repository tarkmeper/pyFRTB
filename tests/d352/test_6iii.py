import math
import FRTB
from tests.trades.fx import FX_OPTION_BARIER

_CFG = {
    "sensitivity": FRTB.D352_1["sensitivity"],
}


def test_132_fx():
    engine = FRTB.init(_CFG)
    engine.add(FX_OPTION_BARIER('GBP', 1.0, 0, 0, 25))
    engine.add(FX_OPTION_BARIER('EUR', 1.0, 0, 0, 45))
    result = engine.calculate()

    assert result["total"] == math.sqrt(25 ** 2 + 45 ** 2 + 2 * 25 * 45 * (0.6 ** 2))
