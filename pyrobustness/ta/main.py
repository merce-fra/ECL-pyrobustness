# coding=utf-8
# import math
import dataclasses
import pprint
import time
import timeit
from fractions import Fraction
from pathlib import Path
from typing import List

import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.ta.creators as creators
import pyrobustness.runs.explorer as explorer
import pyrobustness.runs.opponentstrategy as opponent_strategy
from benchmarks.bench_explorer import three_clock_automata_1_explo, three_clock_automata_2_explo
from pyrobustness.runs.backtrack_log import BacktrackHTMLLogger, \
    BacktrackConsoleLogger, BacktrackHTMLLoggerBis
from pyrobustness.dtype import Location, Valuation
from benchmarks.bench_automata import formats_0, formats_1, formats_tech, formats_1_with_cycle, formats_non_branch_free, \
    bug_example_t_a


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


def format_same_guard_explo(interval_sampling_precision: int,
                            valuation: Valuation,
                            location: Location):
    return formats_0_exploration(2, interval_sampling_precision, valuation, location)


def formats_1_exploration(interval_sampling_precision: int, valuation: Valuation, location: Location):
    return explorer.Backtracking(ta=formats_1(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 )


def formats_tech_exploration(interval_sampling_precision: int, valuation: Valuation, location: Location):
    return explorer.Backtracking(ta=formats_tech(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 )


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


def formats_2_exploration(interval_sampling_precision: int, valuation: Valuation, location: Location):
    print_class = BacktrackHTMLLogger(file="log.html")
    bb = explorer.Backtracking(ta=formats_1(),
                               start=timed_auto.Configuration(location=location, valuation=valuation),
                               strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                               interval_sampling_step=Fraction(1, interval_sampling_precision),
                               print_class=print_class
                               )
    res = bb.backtracking(to_print=True)
    print_class.emit()

    return res


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


def ta1():
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
                            ],
                        },
                        "resets": [],
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
                                        "lower_bound": 0,
                                        "upper_bound": 1,
                                        "clock_index": 1
                                    }
                                }
                            ]
                        },
                        "resets": [1],
                    }
                ]
            },
            {
                "start_location": 2,
                "end_location": 3,
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
        "goal_location": 3,
        "number_clocks": 2
    })


def ta1_explo(interval_sampling_precision: int,
              valuation: Valuation,
              location: Location):
    return explorer.Backtracking(ta=ta1(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 )


def ta4():
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
                                        "clock_index": 1
                                    }
                                },
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
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 2
    })


def ta4_explo(interval_sampling_precision: int,
              valuation: Valuation,
              location: Location):
    return explorer.Backtracking(ta=ta4(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 )


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


@dataclasses.dataclass
class ExperimentalData(object):
    name: str
    nb_transition: int
    precision: Fraction
    runtime: float
    result: Fraction
    nb_exec: int

    def __str__(self):
        return f"{self.name};{self.nb_transition};{self.precision};{self.runtime};{self.result};{self.nb_exec}"


def experiment_runtime(file="./experiment_f0.csv"):
    max_transition = 6
    max_precision = 7
    nb_exec = 1
    experimental_data: List[ExperimentalData] = []

    for precision_denom in range(1, max_precision + 1):
        for transition in range(1, max_transition + 1):
            t0 = time.time()
            res = formats_0_exploration(transition, precision_denom, [0, 0], 0).backtracking()
            t1 = time.time()
            experimental_data.append(ExperimentalData(f"f0_exploration_{transition}_{precision_denom}",
                                                      transition,
                                                      Fraction(1, precision_denom),
                                                      t1 - t0,
                                                      res.compute_trace_permissiveness(),
                                                      nb_exec
                                                      ))

        t0 = time.time()
        res = formats_1_exploration(precision_denom, [0, 0], 0).backtracking()
        t1 = time.time()
        experimental_data.append(ExperimentalData(f"f1_exploration_{precision_denom}",
                                                  2,
                                                  Fraction(1, precision_denom),
                                                  t1 - t0,
                                                  res.compute_trace_permissiveness(),
                                                  nb_exec
                                                  ))

        t0 = time.time()
        res = formats_tech_exploration(precision_denom, [0, 0], 0).backtracking()
        t1 = time.time()
        experimental_data.append(ExperimentalData(f"f2_exploration_{precision_denom}",
                                                  2,
                                                  Fraction(1, precision_denom),
                                                  t1 - t0,
                                                  res.compute_trace_permissiveness(),
                                                  nb_exec
                                                  ))

    with open(file, 'w') as f:
        f.write("name;nb_transition;precision;runtime;result;nb_exec\n")
        for data in experimental_data:
            f.write(str(data) + "\n")


def experiment_runtime_4_auto(file="./experiment_f0_4auto.csv"):
    nb_exec = 1
    experimental_data: List[ExperimentalData] = []

    for precision_denom in [2, 15]:
        for explo, name in [
            # (ta1_explo, "ta1"),
            # (formats_1_exploration, "ta3"),
            # (format_same_guard_explo, "ta2"),
            # (ta4_explo, "ta4"),
            (three_clock_automata_1_explo, "3clock_6_21b"),
            (three_clock_automata_2_explo, "3clock_6_21c"),
        ]:
            t0 = time.time()
            res = explo(precision_denom, [0, 0, 0], 0).backtracking()
            t1 = time.time()
            experimental_data.append(ExperimentalData(f"{name}_exploration_{precision_denom}",
                                                      2,
                                                      Fraction(1, precision_denom),
                                                      t1 - t0,
                                                      res.compute_trace_permissiveness(),
                                                      nb_exec
                                                      ))

    with open(file, 'w') as f:
        f.write("name;nb_transition;precision;runtime;result;nb_exec\n")
        for data in experimental_data:
            f.write(str(data) + "\n")


def logger_exp():
    explorator = formats_1_exploration(2, [0, 0], 0)
    explorator.print_class = BacktrackHTMLLogger("./log.html")

    explorator.backtracking(to_print=True)

    explorator.print_class.emit()


@dataclasses.dataclass
class PrecisionExpData(object):
    name: str
    precision: int
    runtime: float
    erreur: Fraction
    valuation: Valuation

    def __str__(self):
        return f"{self.name};{self.valuation};{self.precision};{self.runtime};{self.erreur}\n"


def experiment_precision():
    location = 0
    valuation = [Fraction(1, 5), Fraction(2, 3)]
    permissivite = Fraction(4, 15)
    config = timed_auto.Configuration(location=location, valuation=valuation)
    file: Path = Path('./experiment_precision_1_5__2_3.csv')

    expRes = []

    for precision_denom in range(1, 200 + 1):
        # print_class = BacktrackHTMLLogger(file=f"log_{precision_denom}.html")
        bb = explorer.Backtracking(ta=formats_1(),
                                   start=config,
                                   strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                   interval_sampling_step=Fraction(1, precision_denom),
                                   #                         print_class=print_class
                                   )
        t0 = time.time()
        res = bb.backtracking(to_print=False)
        t1 = time.time()

        # print_class.emit()

        erreur = res.compute_trace_permissiveness() - permissivite

        expRes.append(
            PrecisionExpData(name="format2", valuation=valuation, precision=precision_denom, runtime=t1 - t0,
                             erreur=erreur))

        print(precision_denom, t1 - t0, erreur)

    with open(file, 'w') as f:
        f.write("name;valuation;precision;runtime;erreur\n")

        for r in expRes:
            f.write(str(r))


def experiment_precision_nbf():
    location = 0
    valuation = [Fraction(1, 4), Fraction(7, 10)]
    permissivite = Fraction(11, 40)
    config = timed_auto.Configuration(location=location, valuation=valuation)
    file: Path = Path('./experiment_precision_nbf_1_4__7_10__perm_11_40.csv')

    expRes = []

    for precision_denom in range(1, 130 + 1):
        # print_class = BacktrackHTMLLogger(file=f"log_{precision_denom}.html")
        t0 = time.time()
        res = formats_non_branch_free_exploration(location=location,
                                                  valuation=valuation,
                                                  interval_sampling_precision=precision_denom,
                                                  delay_sampling_precision=precision_denom
                                                  )
        t1 = time.time()

        # print_class.emit()

        erreur = res.compute_trace_permissiveness() - permissivite

        expRes.append(
            PrecisionExpData(name="non_branch_free", valuation=valuation, precision=precision_denom, runtime=t1 - t0,
                             erreur=erreur))

        print(precision_denom, t1 - t0, erreur)

    with open(file, 'w') as f:
        f.write("name;valuation;precision;runtime;erreur\n")

        for r in expRes:
            f.write(str(r))


def experiment_long_three_clocks_ta_explo(location,
                                          valuation,
                                          interval_sampling_precision,
                                          resets: List[List]):
    # resets = [ [], [], [], [] ]
    transitions = [
        {
            "start_location": 0,
            "end_location": 1,
            "data": [{
                "action": "a_" + str(0),
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
                        },
                        {
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 2
                            }
                        }

                    ],
                },
                "resets": resets[0],  # [2],
            }],
        },

        {
            "start_location": 1,
            "end_location": 2,
            "data": [{
                "action": "a_" + str(1),
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
                        },
                        {
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 2
                            }
                        }

                    ],
                },
                "resets": resets[1],  # [1],
            }],
        },
        {
            "start_location": 2,
            "end_location": 3,
            "data": [{
                "action": "a_" + str(2),
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
                        },
                        {
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 2
                            }
                        }

                    ],
                },
                "resets": resets[2],  # [],
            }],
        },
        {
            "start_location": 3,
            "end_location": 4,
            "data": [{
                "action": "a_" + str(3),
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
                        },
                        {
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 2
                            }
                        }

                    ],
                },
                "resets": resets[3],  # [],
            }],
        }

    ]

    ta_3_clocks = creators.timed_automaton_creator({
        "transitions": transitions
        ,
        "init_location": 0,
        "goal_location": 4,
        "number_clocks": 3
    })

    bb = explorer.Backtracking(ta=ta_3_clocks,
                               start=timed_auto.Configuration(location=location, valuation=valuation),
                               strategy_opponent=
                               opponent_strategy.worst_case_branch_free_opponent_strategy(),
                               interval_sampling_step=Fraction(1, interval_sampling_precision),
                               ).backtracking()
    return bb


def experiment_long_three_clocks_ta(location,
                                    valuation,
                                    interval_sampling_precision,
                                    resets: List[List]):
    # file: Path = Path('./experiment-three-clocks-ta.csv')
    t0 = time.time()
    res = experiment_long_three_clocks_ta_explo(location=location,
                                                valuation=valuation,
                                                interval_sampling_precision=interval_sampling_precision,
                                                resets=resets)
    t1 = time.time()

    res = res.compute_trace_permissiveness()
    print("valuation = " + str(valuation) + ", res = " + str(res) + ", precision = " + str(
        interval_sampling_precision) + " runtime = " + str(t1 - t0))


def main():
    """
    BLOC FORMATS NON-FREE TA
    """
    """
    BLOC TA WITH CYCLE
    

    pprint.pprint(formats_1_with_cycle_exploration(interval_sampling_precision=2,
                         (dire                          
                         delay_sampling_precision=1,
                                                   valuation=[0, 0],
                                                   location=0))
    """

    """
    BLOC FORMATS FIRST T.A FORMATS_0, comment to gain performance!
    """
    max_transition = 2
    timing_tab = [0 for i in range(1, max_transition)]
    for i in range(1, max_transition):
        # start of operation
        timing_tab[i - 1] = timeit.timeit(
            "formats_0_exploration(" + str(i) + ", " + str(i) + ", [0,0], 0).backtracking()",
            number=1,
            globals=globals())
        # print(bt)
        # pprint.pprint(explorer.Trace.compute_trace_permissiveness(bt))
        # end of operation

    pprint.pprint(timing_tab)
    """ BLOC: Evaluation of thew experimental complexity
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
    # pprint.pprint(formats_2_exploration(interval_sampling_precision=2,
    #                                     valuation=[0, 0],
    #                                     location=0))


if __name__ == "__main__":
    # execute only if run as a script
    # main()
    # experiment_runtime()
    # experiment_precision_nbf()
    # val = [1, Fraction(1, 3), Fraction(1, 10)]
    # experiment_long_three_clocks_ta(0, val, 10, [[2], [1], [], []])
    experiment_runtime_4_auto()
    # logger_exp()
