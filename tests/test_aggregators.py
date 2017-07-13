import numpy
import pytest

from FRTB import aggregators as agg


def test_constant_aggregator():
    n = numpy.array([1, -2, 3])
    value = agg.constant_aggregator(n, 1)
    assert value == pytest.approx((1 - 2 + 3) ** 2)

    n = numpy.array([1, -2, 3])
    value = agg.constant_aggregator(n, 0.3)
    assert value == pytest.approx(11)


def test_matrix_aggregator():
    n = numpy.array([1, -2, 3])
    m = numpy.array([
        [1, 0.3, 0.3],
        [0.3, 1, 0.3],
        [0.3, 0.3, 1],
    ])
    value = agg.matrix_aggregator(n, m)
    assert value == pytest.approx(11)
