import FRTB

CFG = {
    "residual": {
        "exotic-products": [
            ("IR", "Exotic")
        ],
        "vanilla-products": [
            ("FX", "Simple Exotic", "Barrier"),
            ("FX", "Simple Exotic", "Digital"),
        ],
        "vanilla-value": 0.1,
        "exotic-value": 1.0
    }
}


def create_trade(notional, asset_class, product, subtype=None, subsubtype=None):
    trade = {
        "Notional": notional,
        "Asset Class": asset_class,
        "Base Product": product,
    }
    if subtype is not None:
        trade["Sub Product"] = subtype
        if subsubtype is not None:
            trade["Sub Sub Type"] = subsubtype
    return trade


def test_empty():
    part, errors = FRTB.append_trades([], {})
    result = FRTB.calculate_capital(part, CFG)
    assert result["total"] == 0.0


def test_non_residual():
    trade = create_trade(1000, "IR", "IR Swap", "Fixed Float")
    part, errors = FRTB.append_trades([trade], {})
    result = FRTB.calculate_capital(part, CFG)
    assert result["total"] == 0.0


def test_residual_exact():
    trade = create_trade(1000, "IR", "Exotic", )
    part, errors = FRTB.append_trades([trade], {})
    result = FRTB.calculate_capital(part, CFG)
    assert result["total"] == 1000.0


def test_residual_approximate():
    trade = create_trade(1000, "IR", "Exotic", "Longevity")
    part, errors = FRTB.append_trades([trade], {})
    result = FRTB.calculate_capital(part, CFG)
    assert result["residual"]["exotic"] == 1000.0
    assert result["residual"]["total"] == 1000.0
    assert result["total"] == 1000.0


def test_residual_vanilla():
    trade = create_trade(1000, "FX", "Simple Exotic", "Barrier")
    part, errors = FRTB.append_trades([trade], {})
    result = FRTB.calculate_capital(part, CFG)
    assert result["residual"]["vanilla"] == 1000.0
    assert result["residual"]["total"] == 100.0
    assert result["total"] == 100.0


def test_multiple_single_call():
    trade1 = create_trade(1000, "FX", "Simple Exotic", "Barrier")
    trade2 = create_trade(1000, "IR", "Exotic", "Longevity")
    trade3 = create_trade(1000, "IR", "Exotic", "Longevity")
    part, errors = FRTB.append_trades([trade1, trade2, trade3], {})
    result = FRTB.calculate_capital(part, CFG)
    assert result["residual"]["vanilla"] == 1000.0
    assert result["residual"]["exotic"] == 2000.0
    assert result["residual"]["total"] == 2100.0
    assert result["total"] == 2100.0


def test_multiple_multiple_call():
    trade1 = create_trade(1000, "FX", "Simple Exotic", "Barrier")
    trade2 = create_trade(1000, "IR", "Exotic", "Longevity")
    trade3 = create_trade(1000, "IR", "Exotic", "Longevity")
    part, errors = FRTB.append_trades([trade1], {})
    part, errors = FRTB.append_trades([trade2, trade3], part)
    result = FRTB.calculate_capital(part, CFG)
    assert result["residual"]["vanilla"] == 1000.0
    assert result["residual"]["exotic"] == 2000.0
    assert result["residual"]["total"] == 2100.0
    assert result["total"] == 2100.0
