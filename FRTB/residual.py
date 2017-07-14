import bisect


def append_residual(trade, part):
    trade_type = None
    if "Sub Sub Product" in trade:
        trade_type = (trade["Asset Class"], trade["Base Product"], trade["Sub Product"], trade["Sub Sub Product"])
    elif "Sub Product" in trade:
        trade_type = (trade["Asset Class"], trade["Base Product"], trade["Sub Product"])
    else:
        trade_type = (trade["Asset Class"], trade["Base Product"])

    if trade_type not in part:
        part[trade_type] = float(trade["Notional"])
    else:
        part[trade_type] += float(trade["Notional"])
    return part


def calculate_residual(part, cfg):
    vanilla_products = ProductSet(cfg["vanilla-products"])
    exotic_products = ProductSet(cfg["exotic-products"])
    exotic_value = vanilla_value = 0

    for entry, notional in part.items():
        if entry in vanilla_products:
            vanilla_value += notional
        elif entry in exotic_products:
            exotic_value += notional

    result = {
        "vanilla": vanilla_value,
        "exotic": exotic_value,
        "total": vanilla_value * cfg["vanilla-value"] + exotic_value * cfg["exotic-value"]
    }
    return result


class ProductSet(object):
    """
    The product set is a container to identify quickly if a specific product is contained within
    a hierarchy.

    It stores the hierarchy as a sorted list and makes use of determining where an entry would be inserted
    to determine if this entry is covered.
    """

    def __init__(self, objects):
        self.values = sorted(objects)

    def __contains__(self, item):
        idx_left = bisect.bisect_left(self.values, item)
        if idx_left < len(self.values) and self.values[idx_left] == item:
            return True
        # Special case - if not exact match and at left hand side there is no match we need to stop.
        elif idx_left == 0:
            return False
        elif len(self.values[idx_left - 1]) < len(item):
            return self.values[idx_left - 1] == item[:len(self.values[idx_left - 1])]
        else:
            return False
