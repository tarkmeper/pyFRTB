from tests.trades.util import delta, curvature, vega


def FX_CASH_TRADE(currency, delta):
    return {
        "notional": 1000, "asset-class": "fx", "base-product": "cash",
        "sensitivity": [
            {"class": "fx", "measure": "delta", "currency": currency, "value": delta},
        ]
    }


def FX_OPTION_BARIER(
        currency,
        option_expiry=1.0,
        fx_delta=25,
        fx_vega=35,
        fx_curvature=35):
    return {
        "notional": 1000, "asset-class": "fx", "base-product": "option", "level2-product": "exotic",
        "maturity": option_expiry,
        "sensitivity": [
            delta('fx', currency, fx_delta),
            curvature('fx', currency, fx_curvature),
            vega('fx', currency, fx_vega, option_expiry),
        ]
    }
