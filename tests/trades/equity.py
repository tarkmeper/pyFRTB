CASH_ABC = {
    "notional": 120000, "asset-class": "equity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "equity", "measure": "delta", "name": "abc", "cap": "large", "economy": "emerging",
         "sector": "financial", "value": 12, "rating": "AA"},
    ],
}

CASH_ABC2 = {
    "notional": 120000, "asset-class": "equity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "equity", "measure": "delta", "name": "abc2", "cap": "large", "economy": "emerging",
         "sector": "financial", "value": 16, "rating": "AA"},
    ]
}

CASH_DEF = {
    "notional": 120000, "asset-class": "equity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "equity", "measure": "delta", "name": "def", "cap": "small", "economy": "advanced",
         "sector": "financial", "value": 17, "rating": "AA"},
    ]
}

CASH_DEF2 = {
    "notional": 120000, "asset-class": "equity", "base-product": "forward", "maturity": 730,
    "sensitivity": [
        {"class": "equity", "measure": "delta", "name": "def2", "cap": "small", "economy": "advanced",
         "sector": "financial", "value": 19, "rating": "AA"},
    ]
}

# todo add vega.
EQUITY_VARIANCE_OPTION = {
    "notional": 120000, "asset-class": "equity", "base-product": "option", "level2-product": "variance",
    "maturity": 730,
    "sensitivity": [
        {"class": "equity", "measure": "delta", "name": "def2", "cap": "small", "economy": "advanced",
         "sector": "financial", "tenor": 30, "value": 19, "rating": "AA"},
    ],
}

TRADE_LIST = [
    CASH_ABC,
    CASH_ABC2,
    CASH_DEF,
    CASH_DEF2,
    EQUITY_VARIANCE_OPTION
]
