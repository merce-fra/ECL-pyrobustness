# coding=utf-8
from fractions import Fraction

import pytest
import pyrobustness.runs.moves as moves
import pyrobustness.ta.guards as guards


# Examples of runs
import pyrobustness.ta.interval


@pytest.fixture(autouse=True)
def run_0():
    pass


@pytest.fixture(autouse=True)
def empty_move():
    return {"action": "a", "step": []}


@pytest.fixture(autouse=True)
def standard_move():
    return {"action": "a", "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1)]}


@pytest.fixture(autouse=True)
def standard_move_expected_sampling_0_5():
    return [
        {
            "action": "a",
            "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1)]
        },
        {
            "action": "a",
            "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, Fraction(1, 2), closed='both'), target_location=1)]
        },
        {
            "action": "a",
            "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(Fraction(1, 2), 1, closed='both'), target_location=1)]
        }
    ]


@pytest.fixture(autouse=True)
def two_step_move():
    return {"action": "a", "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1),
                                    moves.Step(interval=pyrobustness.ta.interval.Interval(1, 5, closed='neither'), target_location=3)]}


@pytest.fixture(autouse=True)
def two_step_move_expected_sampling_1():
    return [{'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 5, closed='neither'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 4, closed='right'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 3, closed='right'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 2, closed='right'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(1, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 4, closed='right'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(1, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 3, closed='right'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(1, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 2, closed='right'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(2, 4, closed='both'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(2, 3, closed='both'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(3, 4, closed='both'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(1, 1, closed='both'), target_location=1),
                      moves.Step(interval=pyrobustness.ta.interval.Interval(1, 5, closed='neither'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(2, 5, closed='left'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(3, 5, closed='left'), target_location=3)]},
            {'action': 'a',
             'step': [moves.Step(interval=pyrobustness.ta.interval.Interval(4, 5, closed='left'), target_location=3)]}]


@pytest.fixture(autouse=True)
def first_move():
    return {"action": "a", "step": [moves.Step(
        interval=pyrobustness.ta.interval.Interval(1, 3, closed='both'),
        target_location=2)]}


@pytest.fixture(autouse=True)
def second_move():
    return {"action": "a", "step": [moves.Step(
        interval=pyrobustness.ta.interval.Interval(4, 5, closed='both'),
        target_location=3)]}


@pytest.fixture(autouse=True)
def third_move():
    return {"action": "a", "step": [moves.Step(
        interval=pyrobustness.ta.interval.Interval(0, 5, closed='both'),
        target_location=3)]}