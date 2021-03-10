# coding=utf-8
from fractions import Fraction

from pyrobustness.ta.interval import Interval
import pytest
from math import inf


# Examples of intervals

@pytest.fixture(autouse=True)
def interval_positive_closed():
    return Interval(0, 5)


@pytest.fixture(autouse=True)
def interval_positive_infinite_closed():
    return Interval(0, inf)


@pytest.fixture(autouse=True)
def interval_positive_open_left():
    return Interval(0, 5, closed='right')


@pytest.fixture(autouse=True)
def interval_positive_open_right():
    return Interval(0, 5, closed='left')


@pytest.fixture(autouse=True)
def interval_positive_open_both():
    return Interval(0, 5, closed='neither')


@pytest.fixture(autouse=True)
def interval_float_bounds():
    return Interval(0, Fraction(21, 10))
