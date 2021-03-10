# coding=utf-8
from math import inf
import pytest
from pyrobustness.ta.interval import Interval
from pyrobustness.ta.creators import linear_constraint_creator, edge_creator, linear_guard_creator, label_creator


# Example of intervals:

@pytest.fixture(autouse=True)
def open_interval_0_4():
    return Interval(0, 4, closed='neither')


@pytest.fixture(autouse=True)
def closed_interval_0_4():
    return Interval(0, 4, closed='both')


@pytest.fixture(autouse=True)
def left_closed_interval_0_4():
    return Interval(0, 4, closed='left')


@pytest.fixture(autouse=True)
def right_closed_interval_0_4():
    return Interval(0, 4, closed='right')


@pytest.fixture(autouse=True)
def open_interval_4_6():
    return Interval(4, 6, closed='neither')


@pytest.fixture(autouse=True)
def closed_interval_4_6():
    return Interval(4, 6, closed='both')


@pytest.fixture(autouse=True)
def left_closed_interval_4_6():
    return Interval(4, 6, closed='left')


@pytest.fixture(autouse=True)
def right_closed_interval_4_6():
    return Interval(4, 6, closed='right')


@pytest.fixture(autouse=True)
def infinite_interval_4_inf():
    return Interval(4, inf, closed='both')


# Examples of constraint


@pytest.fixture(autouse=True)
def linear_constraint_standard():
    return linear_constraint_creator(
        lower_bound=0,
        upper_bound=1,
        clock_index=0
    )


@pytest.fixture(autouse=True)
def linear_constraint_standard_third_clock():
    return linear_constraint_creator(
        lower_bound=11,
        upper_bound=30,
        clock_index=3
    )


@pytest.fixture(autouse=True)
def linear_constraint_infinite_bounds():
    return linear_constraint_creator(
        lower_bound=0,
        upper_bound=inf,
        clock_index=1
    )


def linear_constraint_negative_bounds():
    return linear_constraint_creator(
        lower_bound=-1,
        upper_bound=3,
        clock_index=0
    )


def linear_constraint_negative_clock_index():
    return linear_constraint_creator(
        lower_bound=0,
        upper_bound=4,
        clock_index=-1
    )


@pytest.fixture(autouse=True)
def linear_constraint_standard_clone():
    return linear_constraint_creator(
        lower_bound=0,
        upper_bound=1,
        clock_index=0
    )


@pytest.fixture(autouse=True)
def linear_constraint_standard_not_clone():
    return linear_constraint_creator(
        lower_bound=0,
        upper_bound=3,
        clock_index=0
    )


# Examples of guard

@pytest.fixture(autouse=True)
def standard_linear_guard():
    return linear_guard_creator(
        [
            {
                "type": "linear",
                "data": {
                    "lower_bound": 0,
                    "upper_bound": 3,
                    "clock_index": 1
                }
            },

            {
                "type": "linear",
                "data": {
                    "lower_bound": 0,
                    "upper_bound": 4,
                    "clock_index": 0
                }
            }
        ]
    )


# Exemple of label:

@pytest.fixture(autouse=True)
def standard_linear_label():
    return label_creator(
        guard_data={
            "type": "linear",
            "constraints": [
                {
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": 3,
                        "clock_index": 1
                    }
                },
                {
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": 4,
                        "clock_index": 0
                    }
                }
            ]
        },
        resets=[]
    )


# Empty set reset transition: tests that empty set of resets works
@pytest.fixture(autouse=True)
def transition_empty_reset():
    return edge_creator({
        "start_location": 0,
        "end_location": 1,
        "data": [{
            "action": "a",
            "guard": {
                "type": "linear",
                "constraints": [{
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": 1,
                        "clock_index": 0
                    }
                }]
            },
            "resets": [],
        }]
    })


# Multiple guards transition: tests that multiple guards works
@pytest.fixture(autouse=True)
def transition_1():
    return edge_creator({
        "start_location": 0,
        "end_location": 1,
        "data": [{
            "action": "b",
            "guard": {
                "type": "linear",
                "constraints": [
                    {
                        "type": "linear",
                        "data": {
                            "lower_bound": 0,
                            "upper_bound": 1,
                            "clock_index": 0
                        }
                    },
                    {
                        "type": "linear",
                        "data": {
                            "lower_bound": 2,
                            "upper_bound": 3,
                            "clock_index": 1
                        }
                    },
                ]
            },
            "resets": [1],
        }]
    })


# Infinite bounds guards transition: Test that infinite value work as guards
@pytest.fixture(autouse=True)
def transition_2():
    return edge_creator({
        "start_location": 0,
        "end_location": 0,
        "data": [{
            "action": "c",
            "guard": {
                "type": "linear",
                "constraints": [{
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": +inf,
                        "clock_index": 0
                    }
                }]
            },
            "resets": [],
        }]
    })


@pytest.fixture(autouse=True)
def transition_0_false():
    return edge_creator({
        "start_location": 0,
        "end_location": 2,
        "data": [{
            "action": "d",
            "guard": {
                "type": "linear",
                "constraints": [{
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": 1,
                        "clock_index": 0
                    }
                }]
            },
            "resets": [],
        }]
    })


@pytest.fixture(autouse=True)
def transitions(transition_empty_reset, transition_2):
    return [transition_empty_reset, transition_2]
