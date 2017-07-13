import FRTB


def test_capital_blank():
    result = FRTB.calculate_capital({}, {})
    assert result["total"] == 0.0
