# coding=utf-8
from __future__ import annotations  # For forward reference typing

from fractions import Fraction
from functools import reduce

import math
from typing import List, Tuple, Optional, Iterator, Union, NamedTuple

from pyrobustness.dtype import Delay
import pyrobustness.ta.guards as guards
import pyrobustness.ta.interval as interval
import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.runs.moves as moves
import pyrobustness.runs.exceptions as exceptions
import networkx as nx
import pyrobustness.runs.backtrack_log as btlog

# TODO: Update that definition
Interval = interval.Interval
Move = Union[moves.Move, moves.MoveAsInterval]
Configuration = timed_auto.Configuration
TimedAutomaton = timed_auto.TimedAutomaton


class TraceNode(NamedTuple):
    configuration: Configuration
    move: Move
    delay: Delay


TraceList = List[TraceNode]


class Trace(object):

    def __init__(self, data: Optional[TraceList], no_trace: bool = False):
        self.data = data
        self.no_trace = no_trace

    def compute_trace_permissiveness(self) -> float:
        """
        Compute the permissiveness associated to a trace
        :param trace: List[Tuple[Configuration, Interval, Delay]]
        :return: the computed permissiveness of the trace
        """
        if self.data is None:
            return -math.inf
        return reduce(lambda acc, t: min(moves.compute_interval_length(t.move),
                                         acc), self.data, math.inf)

    def compare_trace(self, other_trace: Trace) -> float:
        """
        Optional: None ou Trace en type
        Function use to compare the trace (in order to choose the best
        interval)
        :param trace:
        :param other_trace:
        :return: float < 0 if other_trace better than trace, float == 0 if
        other_trace and trace are equivalent, float > 0 else
        """
        if other_trace.data is None:
            return 1.  # = the other_trace is useless or the other_trace is a non reachable path
        elif self.data is None:
            return -1.
        trace_perm = self.compute_trace_permissiveness()
        other_trace_perm = other_trace.compute_trace_permissiveness()
        return trace_perm - other_trace_perm

    def add_node(self, node: TraceNode) -> Trace:
        return Trace(data=self.data + [node], no_trace=self.no_trace)

    def copy(self):
        return Trace(self.data[:] if self.data is not None else None, self.no_trace)

    def __iter__(self):
        if self.data is None:
            return self
        else:
            return self.data.__iter__()

    def __next__(self):
        raise StopIteration

    def __len__(self):
        if self.data is None:
            return 0
        else:
            return len(self.data)

    def __repr__(self):
        return "Trace(data="+str(self.data)+", no_trace="+str(self.no_trace)+")"


class Backtracking(object):

    def __init__(self, ta: TimedAutomaton,
                 start: Configuration,
                 strategy_opponent,
                 interval_sampling_step: Union[Fraction, int],
                 strategy_player=moves.move_sampling,
                 to_print: bool = False,
                 print_class=None,
                 trace_bound: int = 50,
                 cycle_bound: int = 50,
                 filter_opt: bool = True):
        self.ta = ta
        self.start = start
        self.strategy_opponent = strategy_opponent
        self.interval_sampling_step = interval_sampling_step
        self.strategy_player = strategy_player
        self.best_trace = Trace(data=None, no_trace=True)
        self.to_print = to_print
        self.bound = self.ta.maximal_lower_bound() + self.ta.maximal_upper_bound()
        self.trace_bound = trace_bound
        self.cycle_bound = cycle_bound
        self.print_class = btlog.BacktrackConsoleLogger() if print_class is None else print_class
        self.filter_opt = filter_opt

    def goal_cond(self, current: Configuration) -> bool:
        return current.location == self.ta.goal_location

    # TODO: Finished and move it in a move class. Tested
    @staticmethod
    def compute_interval_length(move) -> float:
        """
        Compute the length of a move

        :param move: a move
        :return: the length of the global interval of the move.
        """
        move_interval = moves.global_interval(move)
        return move_interval.right - move_interval.left

    # @staticmethod
    # def compute_trace_permissiveness(trace: Optional[TraceList]) -> float:
    #     """
    #     Compute the permissiveness associated to a trace
    #     :param trace: List[Tuple[Configuration, Interval, Delay]]
    #     :return: the computed permissiveness of the trace
    #     """
    #     if trace is None:
    #         return -math.inf
    #     return reduce(lambda acc, t: min(moves.compute_interval_length(t[1]),
    #                                      acc), trace, math.inf)
    # acc: the min length of the previous intervals
    # trace: the sequence to apply the function
    # math.inf : the initial value to start the reduction
    # reduce ( F, [a,b,c] ) returns F( F(a,b), c)

    # @staticmethod
    # def compare_trace(trace: Trace,
    #                   other_trace: Trace) -> float:
    #     """
    #     Optional: None ou Trace en type
    #     Function use to compare the trace (in order to choose the best
    #     interval)
    #     :param trace:
    #     :param other_trace:
    #     :return: float < 0 if other_trace better than trace, float == 0 if
    #     other_trace and trace are equivalent, float > 0 else
    #     """
    #     if other_trace.trace is None:
    #         return 1.  # = the other_trace is useless or the other_trace is a non reachable path
    #     elif trace.trace is None:
    #         return -1.
    #     trace_perm = trace.compute_trace_permissiveness()
    #     other_trace_perm = other_trace.compute_trace_permissiveness()
    #     return trace_perm - other_trace_perm

    def print_debug(self, part: btlog.DebugPart, **kwargs):
        if self.to_print:
            self.print_class(part, **kwargs)

    def apply_goal(self, trace: Trace) -> Trace:
        return trace

    def check_cycle_bound(self, trace: Trace) -> None:
        visited_location = {}
        for t in trace:
            location = t[0].location
            visited_location[location] = visited_location.get(location, 0) + 1
            if visited_location[location] >= self.cycle_bound:
                self.print_debug(btlog.DebugPart.CYCLE_EXCEPTION, trace=trace, e=None)
                raise exceptions.CycleException()

    def check_fail(self, trace: Trace) -> None:
        if trace.data is None:
            return
        elif len(trace.data) >= self.trace_bound:
            self.print_debug(btlog.DebugPart.BOUND_EXCEPTION, trace=trace, e=None)
            raise exceptions.BoundException()

        self.check_cycle_bound(trace)

    def filter_poss(self, possibility_move: Move, best_trace: Trace) -> bool:
        """
        Filter the possibility in order to eliminate path that can not improve
        the result
        :param best_trace:
        :param possibility_move:
        :return: True if the possibility must be treated, False otherwise
        """

        if not self.filter_opt:
            # If the filter optimization is not enabled
            return True

        global_interval = moves.global_interval(possibility_move)
        if global_interval.right - global_interval.left > best_trace.compute_trace_permissiveness():
            return True
        return False

    def extract_max_moves(self, current: Configuration) -> \
            List[Move]:
        """
        Extract all the moves associated with the greatest intervals of each
        guards.

        :param current: the current configuration
        :return: a list of moves
        """
        return moves.moves(self.ta, current)

    def gen_next_poss(self, current: Configuration) -> Iterator[Move]:
        """
        Return a generators of possible moves.
        :param current: our current configuration
        :return: a generator of moves.
        """
        extracted_max_moves = self.extract_max_moves(current)
        for max_move in extracted_max_moves:
            for sampled_moves in self.strategy_player(
                    move=max_move, strat_sampling=self.interval_sampling_step, bound=self.bound):
                yield sampled_moves

    # TODO: Improvement do not take **kwargs strat yet
    # TODO: change Delay into delay moves
    #  completely the trace in the _backtrack_delay function
    def sampling_opponent(self, next_poss: Move) -> List[Move]:
        """

        Sample delays provided by second player from intervals provided by
        the first player (sampling_opponent est deja pris...)
        :param next_poss: a move
        :return:
        """
        return self.strategy_opponent(next_poss)

    # TODO: get back the best strategy for the best strategy of the player.
    def _backtrack_delay(self, current: Configuration, trace: Trace,
                         move: Move) -> Iterator[Trace]:
        for delay_move in self.sampling_opponent(move):
            next_config = moves.next_step(timed_automaton=self.ta, configuration=current, delay_move=delay_move)
            delay: Delay = delay_move["step"][0].interval
            next_trace: Trace = trace.add_node(TraceNode(configuration=current, move=move, delay=delay))

            if next_config.location == self.ta.goal_location:
                self.print_debug(btlog.DebugPart.START_DELAY, trace=trace, delay=delay)
                self.print_debug(btlog.DebugPart.GOAL_REACHED, trace=trace)
                yield next_trace
            else:
                self.print_debug(btlog.DebugPart.START_DELAY, trace=trace, delay=delay)
                try:
                    yield self._backtrack(next_config, next_trace)
                except exceptions.CycleException:
                    continue

    def _backtrack(self,
                   current: Configuration,
                   trace: Trace) -> Trace:
        if self.goal_cond(current):
            self.apply_goal(trace)
        self.check_fail(trace)

        self.print_debug(part=btlog.DebugPart.START_CONFIG,
                         config=current,
                         trace=trace,
                         perm=trace.compute_trace_permissiveness())

        best_trace: Trace = Trace(data=None, no_trace=True)
        acc_max = []
        for next_poss in self.gen_next_poss(current):
            interval_move = moves.global_interval(next_poss)
            self.print_debug(part=btlog.DebugPart.START_INTERVAL,
                             trace=trace,
                             action=next_poss["action"],
                             interval=interval_move)
            if not self.filter_poss(next_poss, best_trace):
                self.print_debug(part=btlog.DebugPart.FILTERED_OUT_INTERVAL,
                                 trace=trace)
                continue
            # Doing the min_trace:
            minimal_trace: Trace = Trace(data=None, no_trace=True)
            acc_min = []  # Debug
            for future_trace in self._backtrack_delay(current, trace, next_poss):
                permissiveness = future_trace.compute_trace_permissiveness()
                self.print_debug(part=btlog.DebugPart.END_DELAY,
                                 trace=trace,
                                 perm=permissiveness)
                acc_min.append(permissiveness)

                if minimal_trace.no_trace:
                    minimal_trace = future_trace.copy()
                elif future_trace.compare_trace(minimal_trace) < 0:
                    # future_trace is more minimal than minimal_trace
                    minimal_trace = future_trace.copy()

                # Short circuit in case the we have a -inf trace
                if self.filter_opt and math.isinf(permissiveness) and permissiveness < 0:
                    break

            permissiveness_interval = minimal_trace.compute_trace_permissiveness()
            self.print_debug(part=btlog.DebugPart.END_ALL_DELAYS,
                             trace=trace,
                             acc_min=acc_min,
                             perm=permissiveness_interval)

            self.print_debug(part=btlog.DebugPart.END_INTERVAL,
                             trace=trace,
                             perm=permissiveness_interval)

            acc_max.append(permissiveness_interval)
            # Doing the max_trace:
            if best_trace.no_trace:
                best_trace = minimal_trace
                # Deepcopy already made

            elif minimal_trace.compare_trace(best_trace) > 0:
                # minimal_trace better than best_trace
                best_trace = minimal_trace

        self.print_debug(part=btlog.DebugPart.END_ALL_INTERVALS,
                         trace=trace,
                         acc_max=acc_max,
                         perm=best_trace.compute_trace_permissiveness())

        return best_trace

    def backtracking(self, to_print=False):

        try:
            self.ta.existence_infinite_weighted_path(location=self.start.location)
        except nx.NetworkXUnbounded:
            raise exceptions.InfinitePathFound

        self.to_print = to_print
        self.best_trace = self._backtrack(self.start, Trace([]))
        return self.best_trace
