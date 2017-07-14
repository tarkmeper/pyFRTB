# from sba import calculate_SBA, append_SBA
# from jtd import calculate_JTD, append_JTD
# from nmrf import calculate_NMRF, append_NMRF,
from .partial import merge_partial
from .residual import calculate_residual, append_residual


def append_trades(trades, part):
    errors = []
    for trade in trades:
        try:
            # partial["SBA"] = append_SBA(trades, partial["SBA"]) if "SBA" in partial else append_SBA(trades, {})
            part["residual"] = append_residual(trade, part["residual"] if "residual" in part else {})
        except AttributeError as e:
            errors += [e]
    return part, errors


def calculate_capital(part, cfg):
    result = {}

    if "residual" in part:
        result["residual"] = calculate_residual(part["residual"], cfg["residual"])

    result["total"] = sum([f["total"] for f in result.values()])
    return result
