import math

import FRTB
from tests.trades.util import delta, curvature, vega

BUCKETS = FRTB.D352_1["sensitivity"]["girr"]["bucket_fields"]["tenor"]["values"]


def IR_SWAP(currency, name, girr_delta):
    sens_list = [
        delta('girr', currency, d, BUCKETS[idx], name, type='yield') for idx, d in enumerate(girr_delta)
    ]
    return {
        "notional": 100, "asset-class": "girr", "base-product": "swap", "maturity": 1400,
        "sensitivity": sens_list
    }


def NON_YIELD_SWAP(currency, name, type, value):
    return {
        "notional": 100, "asset-class": "girr", "base-product": "swap", "maturity": 1400, 'level2-product': 'inflation',
        "sensitivity": [
            {
                "class": 'girr', "measure": "delta", "currency": currency, "value": value, "tenor": None,
                "name": name, "type": type
            }
        ]
    }


def BERMUDA_SWAPTION_CAD(currency, name, option_tenor, underlying_tenor, d_vect, c, v):
    sens_list = [
        delta('girr', currency, d, BUCKETS[idx], name, type='yield') for idx, d in enumerate(d_vect)
    ]
    sens_list += [
        curvature('girr', currency, c, name),
        vega('girr', currency, v, option_tenor, underlying_tenor )
    ]
    return {
        "notional": 1000, "asset-class": "girr", "base-product": "exotic", "level2-product": "longevity", "maturity": 350,
        "sensitivity": sens_list
    }


# Todo add Vega's
IR_BERMUDA_SWAPTION_CAD = {
    "notional": 1000, "asset-class": "girr", "base-product": "option", "sub-product": "swaption",
    "sub-sub-product": "bermuda", "maturity": 350,
    "sensitivity": [
        # CAD leg sensitivities
        {"class": "girr", "measure": "delta", "type": "yield", "name": "cad 3m", "currency": "CAD", "tenor": 1.0,
         "value": 19},

        # Vega
        {"class": "girr", "measure": "vega", "type": "yield", "name": "cad 3m", "currency": "CAD",
         "tenor": 1.0, "underlying-tenor": 800, "value": 31},
    ]
}
