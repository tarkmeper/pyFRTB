import FRTB
from tests.trades.equity import EQUITY_VARIANCE_OPTION
from tests.trades.commodity import WEATHER_OPTION


_CFG = {
    'residual': FRTB.D352_1["residual"],
}

_expected_eq = EQUITY_VARIANCE_OPTION["notional"] * FRTB.D352_1["residual"]["vanilla-value"]
_expected_weather = WEATHER_OPTION["notional"] * FRTB.D352_1["residual"]["exotic-value"]


def test_58_empty():
    engine = FRTB.init(_CFG)
    result = engine.calculate()
    assert result["residual"]["total"] == 0.0
    assert result["total"] == 0.0


def test_58_non_residual():
    engine = FRTB.init(_CFG)
    result = engine.calculate()
    assert result["residual"]["total"] == 0.0


def test_58c_exotic():
    engine = FRTB.init(_CFG)
    engine.add(WEATHER_OPTION)
    result = engine.calculate()

    assert result["total"] == _expected_weather


def test_58c_vanilla():
    engine = FRTB.init(_CFG)
    engine.add(EQUITY_VARIANCE_OPTION)
    result = engine.calculate()

    assert result["total"] == _expected_eq


def test_58c_combined():
    engine = FRTB.init(_CFG)
    engine.add(WEATHER_OPTION)
    engine.add(EQUITY_VARIANCE_OPTION)
    result = engine.calculate()

    assert result["total"] == _expected_eq + _expected_weather
