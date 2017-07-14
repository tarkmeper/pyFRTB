import functools

import FRTB


def test_blank():
    result = FRTB.merge_partial({}, {})
    assert result == {}


def test_merge_keys():
    a = {"x": 12, "a": 1}
    b = {"x": 24, "b": 2}
    result = FRTB.merge_partial(a, b)
    assert result == {"x": 36, "a": 1, "b": 2}


def test_nested():
    a = {"first": {"x": 12, "a": 1, "third": {"c": 1, "fourth": {}}}}
    b = {"first": {"x": 24, "b": 2, "third": {"c": 1, "fourth": {}}}}
    result = FRTB.merge_partial(a, b)
    assert result == {"first": {"x": 36, "a": 1, "b": 2, "third": {"c": 2, "fourth": {}}}}


def test_reduce():
    # Quick test to makesure that FRTB.merge_partial works with reduce function it should
    a = {"first": {"x": 12, "a": 1, "third": {"c": 1, "fourth": {}}}}
    b = {"first": {"x": 24, "b": 2, "third": {"c": 1, "fourth": {}}}}
    result = functools.reduce(FRTB.merge_partial, [{}, a, b])
    assert result == {"first": {"x": 36, "a": 1, "b": 2, "third": {"c": 2, "fourth": {}}}}
