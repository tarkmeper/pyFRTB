import math
import pytest


def get_pair_expected(a, b, corr, sens=None):
    result = math.sqrt(a ** 2 + b ** 2 + 2 * a * b * corr)
    return pytest.approx(result, sens)
