# coding = utf-8
from fractions import Fraction

import pytest
import pyrobustness.runs.moves as moves
import pyrobustness.ta.guards as guards
import pyrobustness.ta.creators as creators
import pyrobustness.runs.explorer as explorer
import pyrobustness.ta.interval
import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.runs.opponentstrategy as strategy
from random import uniform
from pyrobustness.ta.timedauto import Configuration
from pyrobustness.runs.explorer import Trace, TraceNode


# Example of moves and sampling moves


@pytest.fixture(autouse=True)
def empty_move():
    return {"action": "a", "step": []}


@pytest.fixture(autouse=True)
def standard_move():
    return {"action": "a", "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'),
                                               target_location=1)]}


@pytest.fixture(autouse=True)
def standard_move_expected_sampling_0_5():
    return [
        {
            "action": "a",
            "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'), target_location=1)]
        },
        {
            "action": "a",
            "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, Fraction(1, 2), closed='both'),
                                target_location=1)]
        },
        {
            "action": "a",
            "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(Fraction(1, 2), 1, closed='both'),
                                target_location=1)]
        }
    ]


@pytest.fixture(autouse=True)
def two_step_move():
    return {"action": "a", "step": [moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1, closed='both'),
                                               target_location=1),
                                    moves.Step(interval=pyrobustness.ta.interval.Interval(1, 5, closed='neither'),
                                               target_location=3)]}


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


# Examples of traces


@pytest.fixture(autouse=True)
def trace_0(two_step_move, standard_move):
    return Trace(data=[
        TraceNode(Configuration(0, [0, 0]), standard_move, 0.5),
        TraceNode(Configuration(0, [0.5, 0.5]), two_step_move, 1.6)])


@pytest.fixture(autouse=True)
def trace_1(first_move, second_move, third_move):
    return Trace(data=[
        TraceNode(Configuration(0, [0, 0]), first_move, 2),
        TraceNode(Configuration(0, [0, 0]), second_move, 4.5)])


@pytest.fixture(autouse=True)
def trace_2(third_move):
    return Trace(data=[
        TraceNode(Configuration(0, [0, 0]), third_move, 2)]
    )


@pytest.fixture(autouse=True)
def trace_199_long(standard_move):
    return Trace(data=[
        TraceNode(Configuration(t, [0, 0]), standard_move, uniform(0, 1))
        for t in range(199)]
    )


@pytest.fixture(autouse=True)
def trace_200_long(third_move):
    return Trace(data=[
        TraceNode(Configuration(t, [0, 0]), third_move, uniform(0, 5))
        for t in range(200)])


@pytest.fixture(autouse=True)
def trace_201_long(third_move):
    return Trace(data=[
        TraceNode(Configuration(t, [0, 0]), third_move, uniform(0, 5))
        for t in range(201)])


@pytest.fixture(autouse=True)
def trace_300_long(third_move):
    return Trace(data=[
        TraceNode(Configuration(t, [0, 0]), third_move, uniform(0, 5))
        for t in range(200)])


# Example of timed_automaton


@pytest.fixture(autouse=True)
def formats_timed_automaton_0():
    return creators.timed_automaton_creator({
        "transitions": [
            {
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
                        }],
                    },
                    "resets": [],
                }],
            },
            {
                "start_location": 1,
                "end_location": 2,
                "data": [{
                    "action": "b",
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
                }],
            },
            {
                "start_location": 2,
                "end_location": 3,
                "data": [{
                    "action": "b",
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
                }],
            }
        ],
        "init_location": 0,
        "goal_location": 3,
        "number_clocks": 1
    })


@pytest.fixture(autouse=True)
def formats_timed_automaton_1():
    return creators.timed_automaton_creator({
        "transitions": [
            {
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
                        },
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 0,
                                    "upper_bound": 1,
                                    "clock_index": 1
                                }
                            }
                        ],
                    },
                    "resets": [1],
                }],
            },
            {
                "start_location": 1,
                "end_location": 2,
                "data": [{
                    "action": "b",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 1,
                                "upper_bound": 2,
                                "clock_index": 0
                            }
                        }]
                    },
                    "resets": [],
                },
                    {
                        "action": "b",
                        "guard": {
                            "type": "linear",
                            "constraints": [{
                                "type": "linear",
                                "data": {
                                    "lower_bound": 1,
                                    "upper_bound": 2,
                                    "clock_index": 1
                                }
                            }]
                        },
                        "resets": [],
                    }],
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


@pytest.fixture(autouse=True)
def formats_timed_automaton_2():
    return creators.timed_automaton_creator({
        "transitions": [
            {
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
                        },
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 0,
                                    "upper_bound": 1,
                                    "clock_index": 1
                                }
                            }
                        ],
                    },
                    "resets": [1],
                }],
            },
            {
                "start_location": 1,
                "end_location": 2,
                "data": [{
                    "action": "b",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 1,
                                "upper_bound": 2,
                                "clock_index": 0
                            }
                        }]
                    },
                    "resets": [],
                },
                    {
                        "action": "b",
                        "guard": {
                            "type": "linear",
                            "constraints": [{
                                "type": "linear",
                                "data": {
                                    "lower_bound": 0,
                                    "upper_bound": 1,
                                    "clock_index": 1
                                }
                            }]
                        },
                        "resets": [],
                    }],
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


# Example of backtracking objects:

@pytest.fixture(autouse=True)
def formats_exploration_0_0(formats_timed_automaton_0):
    return explorer.Backtracking(ta=formats_timed_automaton_0,
                                 start=timed_auto.Configuration(location=0, valuation=[0]),
                                 strategy_opponent=strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, 2)
                                 )


@pytest.fixture(autouse=True)
def formats_exploration_1_0(formats_timed_automaton_1):
    return explorer.Backtracking(ta=formats_timed_automaton_1,
                                 start=timed_auto.Configuration(location=0, valuation=[0, 0]),
                                 strategy_opponent=strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, 2)
                                 )


@pytest.fixture(autouse=True)
def formats_exploration_2_0(formats_timed_automaton_2):
    return explorer.Backtracking(ta=formats_timed_automaton_2,
                                 start=timed_auto.Configuration(location=0, valuation=[Fraction(1, 2), 0]),
                                 strategy_opponent=strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, 2)
                                 )


# Example of 'currently running' backtracking objects.


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_0_none_trace(formats_exploration_0_0):
    return formats_exploration_0_0


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_0_better_trace(formats_timed_automaton_0):
    pass


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_0_worst_trace(formats_timed_automaton_0):
    pass


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_1_better_trace(formats_timed_automaton_0):
    pass


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_1_worst_trace(formats_timed_automaton_0):
    pass


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_2_better_trace(formats_timed_automaton_0):
    pass


@pytest.fixture(autouse=True)
def formats_exploration_0_trace_step_worst_trace(formats_timed_automaton_0):
    pass


# Example for filter_poss function test

# Example of fromats_Exploration_with_integer_coefficients

@pytest.fixture(autouse=True)
def formats_exploration_0_precise():
    formats_0 = creators.timed_automaton_creator({
        "transitions": [
            {
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
                                "upper_bound": 3,
                                "clock_index": 0
                            }
                        }],
                    },
                    "resets": [],
                }],
            },
            {
                "start_location": 1,
                "end_location": 2,
                "data": [{
                    "action": "b",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 3,
                                "clock_index": 0
                            }
                        }]
                    },
                    "resets": [],
                }],
            },
            {
                "start_location": 2,
                "end_location": 3,
                "data": [{
                    "action": "c",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 3,
                                "clock_index": 0
                            }
                        }]
                    },
                    "resets": [],
                }],
            }
        ],
        "init_location": 0,
        "goal_location": 3,
        "number_clocks": 1
    })
    return explorer.Backtracking(ta=formats_0,
                                 start=timed_auto.Configuration(location=0, valuation=[0]),
                                 strategy_opponent=strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=1
                                 )


# @pytest.fixture(autouse=True)
# def formats_exploration_2_precise(formats_timed_automaton_2, valuation, strat_sampling):
#     return explorer.Backtracking(ta=formats_timed_automaton_2,
#                                  start=timedauto.Configuration(location=0, valuation=valuation),
#                                  strat_opponent=strategy.worst_case_branch_free_opponent_strategy(),
#                                  strat_sampling=strat_sampling
#                                  )
