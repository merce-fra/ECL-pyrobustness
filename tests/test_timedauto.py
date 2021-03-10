# coding=utf-8
from tests.test_timedauto_examples import *
from pyrobustness.ta.timedauto import *
from pyrobustness.ta.exceptions import *


# TODO(Test for each method at least two examples to verify its accuracy.)
# TODO(Test each exception.)
# TODO(Covering code): CHECK, Next step: make a file to give T+N+D a look.
# TODO(Parameter tab)


class TestEdgeForm:
    def test_edge_form(self, transition_empty_reset, transition_1,
                       transition_2):
        # Test of transition_of_edge
        assert edge_form(transition_empty_reset) == (
            0,
            1,
            {
                "a": label_creator(
                        guard_data={
                            "type": "linear",
                            "constraints": [{
                                "type": "linear",
                                "data": {
                                    'clock_index': 0,
                                    'lower_bound': 0,
                                    'upper_bound': 1,
                                }
                            }]
                        },
                        resets=[]
                    ),
            }
        )
        assert edge_form(transition_2) == (
            0,
            0,
            {
                "c": label_creator(
                    guard_data={
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                'clock_index': 0,
                                'lower_bound': 0,
                                'upper_bound': inf
                            },
                        }],
                    },
                    resets=[]
                )
            }
        )

        # Multiple guards:
        assert edge_form(transition_1) == (
            0,
            1,
            {
                "b": label_creator(
                    guard_data={
                        "type": "linear",
                        "constraints": [
                            {
                                "type": "linear",
                                "data": dict(
                                    clock_index=0,
                                    lower_bound=0,
                                    upper_bound=1
                                ),
                            },
                            {
                                "type": "linear",
                                "data": dict(
                                    clock_index=1,
                                    lower_bound=2,
                                    upper_bound=3
                                ),
                            }
                        ]
                    },
                    resets=[1]
                )
            }
        )

        # Test of transitions_to_edges

    def test_transitions_to_edges(self, transitions):
        assert edges_form(transitions) == [
            (
                0,
                1,
                {
                    "a": label_creator(
                            guard_data={
                                "type": "linear",
                                "constraints": [{
                                    "type": "linear",
                                    "data": dict(
                                        clock_index=0,
                                        lower_bound=0,
                                        upper_bound=1)
                                }]
                            },
                            resets=[]
                    )
                }
            ),
            (
                0,
                0,
                {
                    "c": label_creator(
                            guard_data={
                                "type": "linear",
                                "constraints": [{
                                    "type": "linear",
                                    "data": {
                                        'clock_index': 0,
                                        'lower_bound': 0,
                                        'upper_bound': inf
                                    }
                                }],
                            },
                            resets=[]
                        )
                }
            )
        ]

    # def test_transition_exceptions(self):
    #     with pytest.raises(GuardNotFoundException):
    #         Label(guard=[], resets=[0])


# Initialisation of timed_automaton examples

# timed_automaton_0 = TimedAutomaton(
#     locations=[0, 1], transitions=[transition_0, transition_2],
#     start_location=0,
#     end_location=1, number_clocks=1)
#
# timed_automaton_1 = TimedAutomaton(
#     locations=[0, 1], transitions=[transition_1], start_location=0,
#     end_location=1, number_clocks=2)
#
# timed_automaton_0_clone = TimedAutomaton(
#     locations=[1, 0], transitions=[transition_2],
#     start_location=0,
#     end_location=1, number_clocks=1)
# timed_automaton_0_clone.add_transitions([transition_0])
# timed_automaton_0_clone.well_formed_graph()

# Same, but the locations change their names
# timed_automaton_0_false_clone = TimedAutomaton(
#     locations=[0, 2], transitions=[transition_2, transition_0_false],
#     start_location=0,
#     end_location=2, number_clocks=1)
# timed_automaton_0_false_clone.well_formed_graph()


class TestTATimedAutomatonMethods:

    def test_init(self, timed_automaton_0, timed_automaton_1):
        # TODO: Checking list that might not be ordered is dangerous and
        # TODO: might result in test failure
        assert list(timed_automaton_0.edges) == [(0, 1), (0, 0)]
        assert list(timed_automaton_0.nodes) == [0, 1]
        assert len(timed_automaton_0.nodes) == 2
        assert timed_automaton_0.init_location == 0
        assert timed_automaton_0.goal_location == 1
        assert timed_automaton_0.number_clocks == 1

        assert list(timed_automaton_1.edges) == [(0, 1)]
        assert list(timed_automaton_1.nodes) == [0, 1]
        assert len(timed_automaton_1.nodes) == 2
        assert timed_automaton_1.init_location == 0
        assert timed_automaton_1.goal_location == 1
        assert timed_automaton_1.number_clocks == 2

    def test_maximal_bound(self, timed_automaton_0, timed_automaton_1, timed_automaton_infinite):
        assert timed_automaton_0.maximal_upper_bound() == 1
        assert math.isinf(timed_automaton_infinite.maximal_upper_bound())
        with pytest.raises(nx.NetworkXUnbounded):
            timed_automaton_infinite.existence_infinite_weighted_path(location=0)

    def test_well_formed_graph(self, timed_automaton_0, timed_automaton_1,
                               timed_automaton_6):
        assert timed_automaton_0.is_well_formed()
        assert timed_automaton_1.is_well_formed()
        assert timed_automaton_6.is_well_formed()

    def test_equality(self, timed_automaton_0, timed_automaton_0_clone):
        assert timed_automaton_0_clone == timed_automaton_0
        assert timed_automaton_0_false_clone != timed_automaton_0
        assert timed_automaton_0_false_guard_1 != timed_automaton_0
        assert timed_automaton_0_false_guard_2 != timed_automaton_0
        assert timed_automaton_0_false_guard_3 != timed_automaton_0
        assert timed_automaton_0_false_reset != timed_automaton_0
        assert timed_automaton_0 != timed_automaton_1
        assert timed_automaton_0 != transition_empty_reset

        # TODO(create some timed automaton)

    # @pytest.xfail("TODO")
    # def test_add_transition(self, timed_automaton_0, transition_1):
    #     # TODO
    #     timed_automaton_0.add_transition(1, 1, transition_1)
    #     assert False

    def test_change_location(self, timed_automaton_loc_0,
                             timed_automaton_loc_1,
                             timed_automaton_loc_2):
        assert timed_automaton_loc_0 == timed_automaton_loc_1
        assert timed_automaton_loc_1 == timed_automaton_loc_2

        # TODO(each exception (create each type of non well formed automaton))
        # TODO(a well formed example)

    def test_well_formed(self):
        with pytest.raises(LocationNotFoundException):
            timed_automaton_creator({
                "transitions": [],
                "init_location": None,
                "goal_location": None,
                "number_clocks": 1
            })
        with pytest.raises(LocationNotFoundException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
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
                                            "lower_bound": 2,
                                            "upper_bound": 3,
                                            "clock_index": 1
                                        }
                                    }
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 2,
                "goal_location": 1,
                "number_clocks": 2
            })

        with pytest.raises(LocationNotFoundException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
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
                                            "lower_bound": 2,
                                            "upper_bound": 3,
                                            "clock_index": 1
                                        }
                                    }
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 2,
                "goal_location": 1,
                "number_clocks": 2,
            })
        with pytest.raises(LocationNotFoundException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
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
                                            "lower_bound": 2,
                                            "upper_bound": 3,
                                            "clock_index": 1
                                        }
                                    }
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 2,
                "number_clocks": 2,
            })
        with pytest.raises(LocationNotFoundException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
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
                                            "lower_bound": 2,
                                            "upper_bound": 3,
                                            "clock_index": 1
                                        }
                                    }
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": "a",
                "number_clocks": 2,
            })

        with pytest.raises(ConstraintNotFoundException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
                            "guard": {
                                "type": "linear",
                                "constraints": []
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 2,
            })

        with pytest.raises(ClockNotFoundException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
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
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 0
            })

        with pytest.raises(IndexOutOfRange):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
                            "guard": {
                                "type": "linear",
                                "constraints": [
                                    {
                                        "type": "linear",
                                        "data": {
                                            "lower_bound": 1,
                                            "upper_bound": 2,
                                            "clock_index": 2
                                        }
                                    },
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 1,
            })
        with pytest.raises(IndexOutOfRange):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
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
                                            "lower_bound": 1,
                                            "upper_bound": 2,
                                            "clock_index": 1
                                        }
                                    }
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 1
            })
        with pytest.raises(NegativeIntervalException):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
                            "guard": {
                                "type": "linear",
                                "constraints": [
                                    {
                                        "type": "linear",
                                        "data": {
                                            "lower_bound": -1,
                                            "upper_bound": 2,
                                            "clock_index": 0
                                        }
                                    },
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 1
            })
        with pytest.raises(IndexOutOfRange):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
                            "guard": {
                                "type": "linear",
                                "constraints": [
                                    {
                                        "type": "linear",
                                        "data": {
                                            "lower_bound": 0,
                                            "upper_bound": 1,
                                            "clock_index": 2
                                        }
                                    },
                                ]
                            },
                            "resets": [1],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 1
            })
        with pytest.raises(IndexOutOfRange):
            timed_automaton_creator({
                "transitions": [
                    {
                        "start_location": 0,
                        "end_location": 1,
                        "data": [{
                            "action": "a",
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
                                ]
                            },
                            "resets": [1, 3],
                        }],
                    }
                ],
                "init_location": 0,
                "goal_location": 1,
                "number_clocks": 1
            })
