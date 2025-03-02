CREDIT_BOND_1 = {
    "notional": 100, "asset-class": "credit", "base-product": "bond", "maturity": 3,
    "sensitivity": [
        {"class": "girr", "measure": "delta", "type": "yield", "name": "cad 3m", "currency": "CAD", "tenor": 1,
         "value": 10},
        {"class": "girr", "measure": "delta", "type": "yield", "name": "cad 3m", "currency": "CAD", "tenor": 2,
         "value": 15},
        {"class": "girr", "measure": "delta", "type": "yield", "name": "cad 3m", "currency": "CAD", "tenor": 3,
         "value": 6},
        {"class": "girr", "measure": "delta", "type": "yield", "name": "cad 3m", "currency": "CAD", "tenor": 5,
         "value": 1},
    ],
    "jtd": [
        {"name": "ABC Holding", "sector": "Technology", "rating": "A", "value": 100, 'seniority': 'senior'},
    ],
}
