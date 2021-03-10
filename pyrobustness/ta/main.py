# coding=utf-8
# import math
import pprint
from fractions import Fraction
from math import inf

import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.ta.creators as creators
import pyrobustness.runs.explorer as explorer
import pyrobustness.runs.opponentstrategy as opponent_strategy
from pyrobustness.runs.backtrack_log import BacktrackHTMLLogger, BacktrackConsoleLogger
from pyrobustness.dtype import Location, Valuation


def same_guard(transition_index):
    return {
        "start_location": transition_index - 1,
        "end_location": transition_index,
        "data": [{
            "action": "a_" + str(transition_index),
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
    }


def formats_0(number_of_transitions: int) -> timed_auto.TimedAutomaton:
    return creators.timed_automaton_creator({
        "transitions": [
            same_guard(i) for i in range(1, number_of_transitions + 1)
        ],
        "init_location": 0,
        "goal_location": number_of_transitions,
        "number_clocks": 1
    })


def formats_0_exploration(number_of_transitions: int,
                          interval_sampling_precision: int,
                          valuation: Valuation,
                          location: Location):
    return explorer.Backtracking(ta=formats_0(number_of_transitions=number_of_transitions),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 to_print=False
                                 )


def formats_1() -> timed_auto.TimedAutomaton:
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
                    },
                ]
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def formats_1_exploration(interval_sampling_precision: int, valuation: Valuation, location: Location):
    return explorer.Backtracking(ta=formats_1(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 )


def formats_1_with_cycle() -> timed_auto.TimedAutomaton:
    return creators.timed_automaton_creator({
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
                                    "upper_bound": 2,
                                    "clock_index": 0
                                }
                            },
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 0,
                                    "upper_bound": 2,
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
                                        "upper_bound": +inf,
                                        "clock_index": 0
                                    }
                                },
                                {
                                    "type": "linear",
                                    "data": {
                                        "lower_bound": 0,
                                        "upper_bound": 2,
                                        "clock_index": 1
                                    }
                                }
                            ]
                        },
                        "resets": [],
                    },
                ]
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def formats_1_with_cycle_exploration(interval_sampling_precision: int, delay_sampling_precision: int,
                                     valuation: Valuation, location: Location):
    # print_class = BacktrackConsoleLogger( file="index.txt" )
    print_class = BacktrackHTMLLogger(file="log.html")
    bb = explorer.Backtracking(ta=formats_1_with_cycle(),
                               start=timed_auto.Configuration(location=location, valuation=valuation),
                               strategy_opponent=opponent_strategy.worst_case_brut_force_opponent_strategy(
                                   step=Fraction(1, delay_sampling_precision)),
                               interval_sampling_step=Fraction(1, interval_sampling_precision),
                               cycle_bound=2,
                               trace_bound=50,
                               print_class=print_class)

    res = bb.backtracking(to_print=True)
    print_class.emit()

    return res


def formats_2() -> timed_auto.TimedAutomaton:
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
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def formats_2_exploration(interval_sampling_precision: int, valuation: Valuation, location: Location):
    return explorer.Backtracking(ta=formats_2(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 to_print=False
                                 )


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


def formats_non_branch_free_exploration(interval_sampling_precision: int,
                                        delay_sampling_precision: int,
                                        valuation: Valuation,
                                        location: Location):
    bb = explorer.Backtracking(ta=formats_non_branch_free(),
                               start=timed_auto.Configuration(location=location, valuation=valuation),
                               strategy_opponent=
                               opponent_strategy.worst_case_brut_force_opponent_strategy(
                                   step=Fraction(1, delay_sampling_precision)),
                               interval_sampling_step=Fraction(1, interval_sampling_precision),
                               ).backtracking()

    return bb


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


def bug_example_t_a_exploration(interval_sampling_precision: int,
                                valuation: Valuation,
                                location: Location):
    # print_class = BacktrackConsoleLogger( file="index.txt" )
    print_class = BacktrackHTMLLogger(file="log.html")
    bb = explorer.Backtracking(ta=bug_example_t_a(),
                               start=timed_auto.Configuration(location=location, valuation=valuation),
                               strategy_opponent=
                               opponent_strategy.worst_case_branch_free_opponent_strategy(),
                               interval_sampling_step=Fraction(1, interval_sampling_precision),
                               cycle_bound=2,
                               trace_bound=50,
                               print_class=print_class)

    res = bb.backtracking(to_print=True)
    print_class.emit()

    return res


def main():
    """
    BLOC FORMATS NON-FREE TA
    """
    """
    BLOC TA WITH CYCLE
    

    pprint.pprint(formats_1_with_cycle_exploration(interval_sampling_precision=2,
                                                   delay_sampling_precision=1,
                                                   valuation=[0, 0],
                                                   location=0))
    """


    """
    BLOC FORMATS FIRST T.A FORMATS_0, comment to gain performance!

    for i in range(1, 5):
        # start of operation
        bt = formats_0_exploration(i, i, [0]).backtracking()
        print(bt)
        pprint.pprint(explorer.Backtracking.compute_trace_permissiveness(bt))
        # end of operation
    """

    """ BLOC: Evaluation of the experimental complexity
        Automata: formats_0
        Parameters: number of transitions & precision step = 1/i, for i from 1 to...
    max_nb_of_transition = 7
    max_precision = 8
    tab_of_timing = [[0 for i in range(1, max_precision)] for j in range(1, max_nb_of_transition)]
    for i in range(1, max_nb_of_transition):
        for j in range(1, max_precision):
            # start of operation
            tab_of_timing[i - 1][j - 1] = timeit.timeit(
                                            "formats_0_exploration(" + str(i) +", " +str(j)+", [0]).backtracking()",
                                            number=1,
                                            globals=globals())
    pprint.pprint(tab_of_timing)
            # end of operation

    """
    """ BLOC FORMATS SECOND T.A FORMATS_1, comment to gain performance!
    """
    # gen_valuation = [
    #     [Fraction(i, j), Fraction(k, l)]
    #     for j in range(1, 4)
    #     for i in range(j)
    #     for l in range(1, 4)
    #     for k in range(l)]
    # for val in gen_valuation:
    #     bt = formats_1_exploration(10, val, 0).backtracking()
    #     # print(bt)
    #     pprint.pprint("formats_1 : valuation = " + str(val[0]) + ", " + str(val[1]) + ", permissiveness = " +
    #                   str(explorer.Backtracking.compute_trace_permissiveness(bt)))

    # bt = formats_1_exploration(precision=2, valuation=[0, 0], location=0).backtracking()
    # formats_1_exploration(precision=120, valuation=[0, Fraction(1,2)], location=0).backtracking()

    """ BLOC FORMATS THIRD T.A FORMATS_2, comment to gain performance!
"""
    # gen_valuation = [
    #         [Fraction(i, j), Fraction(k, l)]
    #         for j in range(1, 4)
    #         for i in range(j)
    #         for l in range(1, 4)
    #         for k in range(l)]
    # for val in gen_valuation:
    #     bt = formats_2_exploration(2, val, 0).backtracking()
    #     #print(bt)
    #     pprint.pprint("formats_2: valuation = " + str(val[0]) + ", " + str(val[1]) + ", permissiveness = " +
    #                   str(explorer.Backtracking.compute_trace_permissiveness(bt)))
    """
    BLOC TA WITH BUGS
    """
    pprint.pprint(bug_example_t_a_exploration(interval_sampling_precision=2,
                                              valuation=[0, 0],
                                              location=0))


if __name__ == "__main__":
    # execute only if run as a script
    main()
