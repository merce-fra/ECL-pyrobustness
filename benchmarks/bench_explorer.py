from fractions import Fraction

from benchmarks.bench_automata import three_clock_automata_2, three_clock_automata_1
from pyrobustness.dtype import Valuation, Location
import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.runs.explorer as explorer
import pyrobustness.runs.opponentstrategy as opponent_strategy


def three_clock_automata_1_explo(interval_sampling_precision: int,
                                 valuation: Valuation,
                                 location: Location):
    return explorer.Backtracking(ta=three_clock_automata_1(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 to_print=False
                                 )


def three_clock_automata_2_explo(interval_sampling_precision: int,
                                 valuation: Valuation,
                                 location: Location):
    return explorer.Backtracking(ta=three_clock_automata_2(),
                                 start=timed_auto.Configuration(location=location, valuation=valuation),
                                 strategy_opponent=opponent_strategy.worst_case_branch_free_opponent_strategy(),
                                 interval_sampling_step=Fraction(1, interval_sampling_precision),
                                 to_print=False
                                 )
