OIL_STRIP = {
    "notional": 120000, "asset-class": "commodity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "commodity", "measure": "delta", "name": "coal", "tenor": 1.0, "value": 12},
        {"class": "commodity", "measure": "delta", "name": "coal", "tenor": 730, "value": 17},
    ]
}

CHARCOAL_STRIP = {
    "notional": 120000, "asset-class": "commodity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "commodity", "measure": "delta", "name": "charcoal", "tenor": 1.0, "value": 11},
        {"class": "commodity", "measure": "delta", "name": "charcoal", "tenor": 730, "value": 19},
    ]
}

GRAIN_STRIP = {
    "notional": 120000, "asset-class": "commodity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "commodity", "measure": "delta", "name": "grain", "tenor": 1.0, "value": 9},
        {"class": "commodity", "measure": "delta", "name": "grain", "tenor": 730, "value": 4},
    ]
}

OILSEED_STRIP = {
    "notional": 120000, "asset-class": "commodity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "commodity", "measure": "delta", "name": "oilseed", "tenor": 1.0, "value": 3},
        {"class": "commodity", "measure": "delta", "name": "oilseed", "tenor": 730, "value": 5},
    ]
}


WEATHER_OPTION = {
    "notional": 120000, "asset-class": "commodity", "base-product": "option", "level2-product": "environmental",
    "level3-product": "weather",
    "maturity": 730,
    "sensitivity": [
        {"class": "commodity", "measure": "delta", "name": "weather", "tenor": 1.0, "value": 22},
        {"class": "commodity", "measure": "vega", "name": "weather", "tenor": 1.0, "value": 14},
    ]
}

TRADE_LIST = [
    OIL_STRIP,
    GRAIN_STRIP,
    WEATHER_OPTION
]
