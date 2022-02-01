from math import inf

import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.ta.creators as creators
from benchmarks.utility import linear_transition_constructor, linear_constructor


def formats_0(number_of_transitions: int) -> timed_auto.TimedAutomaton:
    automaton_data = [
        (
            {
                0: (0, 1),
                1: (0, 1)
            },
            []
        ) for i in range(number_of_transitions)
    ]
    return creators.timed_automaton_creator(linear_constructor(automaton_data))


def formats_1() -> timed_auto.TimedAutomaton:
    automaton_data = [
        (
            {
                0: (0, 1),
                1: (0, 1),
            },
            [1]
        ),
        (
            {
                0: (1, 2),
                1: (0, 1),
            },
            []
        ),
    ]
    return creators.timed_automaton_creator(linear_constructor(automaton_data))


def formats_tech() -> timed_auto.TimedAutomaton:
    automaton_data = [
        (
            {
                1: (0, 1),
            },
            [1]
        ),
        (
            {
                0: (1, 2),
                1: (0, 1),
            },
            []
        ),
    ]
    return creators.timed_automaton_creator(linear_constructor(automaton_data))


def formats_1_with_cycle() -> timed_auto.TimedAutomaton:
    automaton_partial_data = [
        (
            {
                0: (0, 2),
                1: (0, 2),
            },
            [1]
        ),
        (
            {
                0: (2, +inf),
                1: (0, 2),
            },
            []
        ),
    ]

    return creators.timed_automaton_creator({
        "transitions": [
                linear_transition_constructor(automaton_partial_data),
            ] + [{
                "start_location": 1,
                "end_location": 1,
                "data": [{
                    "action": "cycle",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 1,
                                "upper_bound": + inf,
                                "clock_index": 0
                            }
                        }
                        ],
                    },
                    "resets": [1],
                }],
            }],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def formats_non_branch_free() -> timed_auto.TimedAutomaton:
    return creators.timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [
                    {
                        "action": "a",
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
                                        "lower_bound": 0,
                                        "upper_bound": 1,
                                        "clock_index": 1
                                    }
                                }
                            ],
                        },
                        "resets": [1],
                    },
                ],
            },
            {
                "start_location": 1,
                "end_location": 2,
                "data": [
                    {
                        "action": "b",
                        "guard": {
                            "type": "linear",
                            "constraints": [
                                {
                                    "type": "linear",
                                    "data": {
                                        "lower_bound": 1,
                                        "upper_bound": 2,
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
                            ]
                        },
                        "resets": [],
                    }
                ]
            },
            {
                "start_location": 0,
                "end_location": 2,
                "data": [
                    {
                        "action": "c",
                        "guard": {
                            "type": "linear",
                            "constraints": [
                                {
                                    "type": "linear",
                                    "data": {
                                        "lower_bound": 1,
                                        "upper_bound": 2,
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
                            ]
                        },
                        "resets": [],
                    }
                ]
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def bug_example_t_a() -> timed_auto.TimedAutomaton:
    return creators.timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [
                    {
                        "action": "a",
                        "guard": {
                            "type": "linear",
                            "constraints": [
                                {
                                    "type": "linear",
                                    "data": {
                                        "lower_bound": 0,
                                        "upper_bound": 2,
                                        "clock_index": 0
                                    }
                                }
                            ],
                        },
                        "resets": [1],
                    },
                ],
            },
            {
                "start_location": 1,
                "end_location": 2,
                "data": [
                    {
                        "action": "b",
                        "guard": {
                            "type": "linear",
                            "constraints": [
                                {
                                    "type": "linear",
                                    "data": {
                                        "lower_bound": 2,
                                        "upper_bound": 6,
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
                            ]
                        },
                        "resets": [],
                    }
                ]
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def three_clock_automata_1() -> timed_auto.TimedAutomaton:
    automaton_data = [
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            []
        ),
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            [1]
        ),
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            []
        ),
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            [2]
        ),
    ]
    return creators.timed_automaton_creator(linear_constructor(automaton_data))


def three_clock_automata_2() -> timed_auto.TimedAutomaton:
    automaton_data = [
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            [2]
        ),
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            [1]
        ),
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            []
        ),
        (
            {
                0: (0, 1),
                1: (0, 1),
                2: (0, 1),
            },
            []
        ),
    ]
    return creators.timed_automaton_creator(linear_constructor(automaton_data))
