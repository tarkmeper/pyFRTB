def delta(cls, currency, value, tenor=None, name=None, type='yield'):
    res = {
        "class": cls, "measure": "delta", "currency": currency, "value": value
    }
    if cls != "fx":
        assert tenor
        res["tenor"] = tenor
    if cls == "girr":
        assert name and type
        res["name"] = name
        res["type"] = type
    return res


def curvature(cls, currency, value, name=None, type='yield'):
    res = {
        "class": cls, "measure": "curvature", "currency": currency, "value": value
    }
    if cls == "girr":
        res["name"] = name
        res["type"] = type
        res["tenor"] = None
    return res


def vega(cls, currency, value, option_tenor, underlying_tenor=None):
    res = {
        "class": cls, "measure": "vega", "currency": currency, "value": value, "option_maturity": option_tenor,
    }
    if cls == "girr":
        res["underlying_maturity"] = underlying_tenor
    return res
