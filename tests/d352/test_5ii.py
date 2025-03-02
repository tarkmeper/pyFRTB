import pytest

import math
import FRTB
from tests.trades.fx import FX_OPTION_BARIER

_CFG = {
    "sensitivity": FRTB.D352_1["sensitivity"],
}


def test_124_fx():
    engine = FRTB.init(_CFG)
    engine.add(FX_OPTION_BARIER('GBP', 1.0, 0, 25, 0))
    result = engine.calculate()

    assert float(result["total"]) == pytest.approx(55 * math.sqrt(40) / math.sqrt(10) * 25)
