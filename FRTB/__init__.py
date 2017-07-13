# from sba import calculate_SBA
# from jtd import calculate_JTD
# from nmrf import calculate_NMRF
from .partial import merge_partial


def calculate_capital(partial, cfg):
    result = {}
    if "SBA" in partial:
        result["sba"] = calculate_SBA(partial["SBA"], cfg["SBA"])

    if "JTD" in partial:
        result["jtd"] = calculate_JTD(partial["NMRF"], cfg["JTD"])

    if "NMRF" in partial:
        result["nmrf"] = calculate_NMRF(partial["NMRF"], cfg["NMRF"])

    result["total"] = sum([f["value"] for f in result.values()])
    return result
