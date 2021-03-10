# coding=utf-8
# TODO: next step with a delay
# TODO: guard pass with an interval
# TODO: next step with an interval + strategy of the opponent (prepare list of
# next step...)
"""
==================================================
Runs module
==================================================

Classes:
------
None

Methods:
valuation_after_passing_guard
valuation_after_passing_guard_permissive
check_continuous_move
global_interval
moves
next_step
move_convertor_permissive_into_delays
next_permissive_step
------
"""
from __future__ import annotations  # For forward reference typing

import math
from typing import Union, List, Dict, Optional
from collections import namedtuple

from pyrobustness.dtype import Delay, Valuation
import pyrobustness.ta.interval as interval
import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.ta.guards as guards
import pyrobustness.runs.exceptions as exceptions

Interval = interval.Interval
Label = guards.Label
Step = namedtuple("Step", ["interval", "target_location"])
Move = Dict[str, Union[str, List[Step]]]
Configuration = timed_auto.Configuration
TimedAutomaton = timed_auto.TimedAutomaton


class MoveAsInterval(object):
    def __init__(self, action, step):
        self.action: str = action
        self.step: List[Step] = step
        self._global_interval = global_interval(self)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def get_as_interval(self):
        return self._global_interval

    def restrict(self, restricted_interval: Interval):
        # Duplicate from move sampling
        interval_step = []
        found_starting_step = False

        if not self._global_interval.include(restricted_interval):
            raise exceptions.IntervalNotFound(interval=str(restricted_interval))

        for step in self.step:
            if restricted_interval.include(step.interval):
            # Condition: the sampled interval is in a single step
                interval_step.append(
                    Step(
                        interval=restricted_interval,
                        target_location=step.target_location
                    )
                )
                break  # Stop searching for useless steps.
            elif (restricted_interval.closed_left and restricted_interval.left in step.interval) \
                    or \
                    (not restricted_interval.closed_left and step.interval.right >
                     restricted_interval.left >= step.interval.left):
                # Condition: the sampled interval begins in this step (
                # but does not finish)

                lowest_type = restricted_interval.closed_left
                highest_type = step.interval.closed_right

                interval_type = Interval.interval_type(
                    lowest_type, highest_type)

                interval_step.append(
                    Step(
                        interval=Interval(
                            restricted_interval.left,
                            step.interval.right,
                            closed=interval_type),
                        target_location=step.target_location
                    )
                )
                found_starting_step = True
            elif (
                    found_starting_step and restricted_interval.closed_right and
                    restricted_interval.right not in step.interval) or \
                    (found_starting_step and not restricted_interval.closed_right and
                     restricted_interval.right > step.interval.right):
                # Condition: upper bound not found yet, keep adding the
                # intermediate steps
                interval_step.append(step)
            elif (
                    found_starting_step and restricted_interval.closed_right and
                    restricted_interval.right in step.interval) or \
                    (
                            found_starting_step and not restricted_interval.closed_right and
                            restricted_interval.right <= step.interval.right):
                # Condition: upper bound found
                lowest_type = step.interval.closed_left
                highest_type = restricted_interval.closed_right
                interval_type = Interval.interval_type(
                    lowest_type, highest_type)
                interval_step.append(
                    Step(
                        interval=Interval(
                            step.interval.left,
                            restricted_interval.right,
                            closed=interval_type),
                        target_location=step.target_location
                    )
                )
                break
                # Interval has been completely found, useless to continue.
            else:
                raise exceptions.IntervalNotFound(interval=str(restricted_interval))

        self._global_interval = restricted_interval
        return MoveAsInterval(action=self.action, step=interval_step)

    def __str__(self):
        return "Move(action="+str(self.action)+", interval="+str(self._global_interval)+")"


def valuation_after_passing_guard(label: Label, valuation: Valuation, delay: Delay) -> Optional[Valuation]:
    """
    This function checks if the delay proposed pass the guard's label label.
    Then if so, it return the valuation of the configuration after passing
    this guard. Let's remark that the reset's label are affected to the
    resulting valuation (see example)

    :param label: an action-label couple of guard and reset: action :{
    guard, reset}.
    :param valuation: an array-like of integer, fraction, or math.inf.
    :param delay: an integer, fraction, or math.inf.
    :return:
    The valuation affected after passing the guard's label and after resets
    the clocks that are in the reset set.
    ------
    Example:
    The label a : { guard: 0 =< x_0 =< 1, 1 =< x_1 =< 2,
    reset : { 0 } }, the valuation [0,1] and the delay 0.5.
    The delay 0.5 pass the guard and the function return [ [0 + 0.5] * 0,
    1 + 0.5 ] = [ 0, 1.5 ] because the first clock is reset.
    ------
    Comment: this function does not depend on the guard type (interval
    constraint, DBM...)
    """

    if label.guard.guard_check(valuation, delay):
        val = [0] * len(valuation)
        for i in range(len(valuation)):
            if i in label.resets:
                val[i] = 0
            else:
                val[i] = valuation[i] + delay
        return val
    return None


def valuation_after_passing_guard_permissive(label: Label, valuation: Valuation,
                                             interval: Interval, strategy, **kwargs) -> List[Optional[Valuation]]:
    """

    :param label: an action-label couple of guard and reset: action :{
    guard, reset}.
    :param valuation: an array-like of integer, fraction, or math.inf.
    :param strategy: the strategy function takes the interval and possible
    parameters and return the list of delay(s) that can be applied by the
    opponent.
    ------
    Example: worst_case_branch_free_opponent_strategy( guards.Interval(0,
    5) ) = [0,5]
    :param interval: an interval (from guards module).
    :return:
    the list of the valuation applied with valuation_after_passing_guard
    function, where the delays are taken in strategy(interval, **kwargs).
    """
    delays = strategy(interval, **kwargs)
    return [valuation_after_passing_guard(label, valuation, delay) for
            delay in delays]


def check_continuous_move(current_move: Move, previous_move: Move) -> bool:
    """
    Checks if current_move and previous_move are continuous: disjoint and concatenable
    Examples: step([3,4], 3) and step((4,6],4)
    Counter-examples: step([3,4], 3) and step([5,6],4) or step([3,4], 3) and step([4,6],4)
    :param current_move: a Move
    :param previous_move: a Move
    :return: a bool
    """
    if current_move["action"] != previous_move["action"]:
        return False
    interval_move = current_move["step"][
        len(current_move["step"])].interval
    interval_previous_move = previous_move["step"][
        len(previous_move["step"])].interval

    return interval_move.left == interval_previous_move.right and (
            interval_move.closed_left or
            interval_previous_move.closed_right)


def global_interval(move: Move) -> Interval:
    """
    return the merge of all the interval of all the steps of a Move.
    :param move: a Move
    :return: an Interval
    """
    return Interval(move["step"][0].interval.left,
                    move["step"][len(move["step"]) - 1].interval.right,
                    closed=Interval.interval_type(
                        move["step"][0].interval.closed_left,
                        move["step"][len(move["step"]) - 1].interval.closed_right
                    ))


def compute_interval_length(move) -> float:
    """
    Compute the length of a move
    :param move: a move
    :return: the length of the global interval of the move.
    """
    interval = global_interval(move)
    return interval.right - interval.left


def moves(timed_automaton: TimedAutomaton,
          config: Configuration) -> List[Move]:
    """
    The function moves takes as input a timed automaton timed_automaton and
    a configuration and compute a list of moves (action, interval) that
    contains for each action of each edges the action-label and the greatest
    interval that can be propose.
    :param timed_automaton: a timed automaton from the module timdauto.
    :param config: a couple (location,valuation) where the location
    is a node of timed_automaton.
    :return: a list of couples (action, interval) that contains for each
    action of each edges the action-label and the greatest interval that can
    be propose.
    ------
    Example:
    TBD
    ------
    Comment: this function highly depends on the timed_automaton type (
    deterministic, branch-free, single_action or not), as :
    1) if the timed_automaton is branch_free, only one action per edge is
    available.
    2) if the timed_automaton is single_action, for each node location and
    action a, only one future guard can the labeled with the action a.
    3) if the timed_automaton is deterministic, the move (delay,action)
    can only leads to one successors.
    4) if not deterministic...one can have many possible successors!

    As a result, the function is only implemented for deterministic
    timed_automaton.
    """

    moves_list = []

    source_location = config.location
    valuation = config.valuation

    if timed_automaton.is_branch_free or timed_automaton.is_single_action():

        for target_location, edge_attr in \
                timed_automaton[source_location].items():
            for action in edge_attr.keys():
                interval = edge_attr[action].guard.enabled_delays_set(valuation)
                moves_list.append({"action": action, "step": [
                    Step(interval=interval, target_location=target_location)]})

    elif timed_automaton.is_deterministic():
        partial_move_list = []

        for target_location, edge_attr in \
                timed_automaton[source_location].items():
            for action, label in edge_attr.item():
                interval = label.guard.enabled_delays_set(valuation)
                partial_move_list.append({"action": action, "step": [
                    Step(interval=interval, target_location=target_location)]})

        # Sort the moves by action and for the same action by the start of
        # their interval
        partial_move_list.sort(
            key=lambda val: (val.action, val.step[0].interval.left)
        )

        # Fusions the moves that can be
        for move in partial_move_list:
            if len(moves_list) == 0:
                moves_list.append(move)
                continue
            pred_move = partial_move_list.pop()
            if check_continuous_move(move, pred_move):
                pred_move["step"].extend(move["step"])
                moves_list.append(pred_move)
            else:
                moves_list.append(pred_move)
                moves_list.append(move)

    else:
        raise exceptions.WrongTimedAutomatonClass(fct="moves",
                                                  ta_class="non-deterministic")

    return moves_list


def next_step(timed_automaton: TimedAutomaton, configuration: Configuration, delay_move: Move) ->\
        Optional[Configuration]:
    """
    The function next_step takes as input a timed automaton timed_automaton,
    a configuration and a delay-move
    :param timed_automaton: a timed automaton.
    :param configuration: a configuration Configuration("location",
    "valuation")
    :param delay_move: a dictionary {"action": action, "step": [
                Step(delay = delay, target_location=target_location)]}
    :return: If the delay pass a guard labelled by action in the edge
    (configuration.location, target, location), the function returns the
    configuration after passing the transition with the delay delay.
    Otherwise, it return None because the delay cannot pass the transition.
    """
    action = delay_move["action"]
    delay = delay_move["step"][0].interval
    target_location = delay_move["step"][0].target_location
    source_location = configuration.location

    if not timed_automaton.is_deterministic:
        raise exceptions.WrongTimedAutomatonClass(fct="next_step",
                                                  ta_class="non-deterministic")
    # check if the target_location is indeed a successor of source_location
    if target_location not in timed_automaton.successors(source_location):
        return None
    # check if the action action is actually labelling an edge between
    # source_location and target_location.
    if action in timed_automaton[source_location][target_location].keys():

        # getting back the {guard, reset} couple that is labelled by action
        label = timed_automaton[source_location][target_location][action]

        # use the valuation_after_passing_guard function
        return timed_auto.Configuration(
            location=target_location,
            valuation=valuation_after_passing_guard(
                label, configuration.valuation, delay))
    else:
        return None


def move_sampling(move, strat_sampling, bound=math.inf):
        """
        Take a move, which type form is {"action": action, "step": List of
                Step(interval=interval, target_location=target_location) }
                and a sampling_step
        :param bound: the bound of the intervals to sample.
        :param move: the move to sample
        :param strat_sampling: a float step
        :return:
        """
        action = move["action"]
        if len(move["step"]) == 0:
            raise exceptions.StepNotFound("No step in the step's list")

        # global_interval represents the merges interval of move

        move_global_interval = global_interval(move)

        # global_interval_sampling represents the sampling the interval
        # global_interval with the step sampling_step

        global_interval_sampling = move_global_interval.semi_sorted_sampling(step=strat_sampling, bound=bound)
        # TODO: add the infinite bound for bounded timed automaton.

        move_sampling_list = []

        for interval in global_interval_sampling:
            interval_step = []
            found_starting_step = False
            for step in move["step"]:
                if interval.include(step.interval):
                    # Condition: the sampled interval is in a single step
                    interval_step.append(
                        Step(
                            interval=interval,
                            target_location=step.target_location
                        )
                    )
                    break  # Stop searching for useless steps.
                elif (interval.closed_left and interval.left in step.interval) \
                        or \
                        (not interval.closed_left and step.interval.right >
                         interval.left >= step.interval.left):
                    # Condition: the sampled interval begins in this step (
                    # but does not finish)

                    lowest_type = interval.closed_left
                    highest_type = step.interval.closed_right

                    interval_type = Interval.interval_type(
                        lowest_type, highest_type)

                    interval_step.append(
                        Step(
                            interval=Interval(
                                interval.left,
                                step.interval.right,
                                closed=interval_type),
                            target_location=step.target_location
                        )
                    )
                    found_starting_step = True
                elif (
                        found_starting_step and interval.closed_right and
                        interval.right not in step.interval) or \
                        (found_starting_step and not interval.closed_right and
                         interval.right > step.interval.right):
                    # Condition: upper bound not found yet, keep adding the
                    # intermediate steps
                    interval_step.append(step)
                elif (
                        found_starting_step and interval.closed_right and
                        interval.right in step.interval) or \
                        (
                                found_starting_step and not interval.closed_right and
                                interval.right <= step.interval.right):
                    # Condition: upper bound found
                    lowest_type = step.interval.closed_left
                    highest_type = interval.closed_right
                    interval_type = Interval.interval_type(
                        lowest_type, highest_type)
                    interval_step.append(
                        Step(
                            interval=Interval(
                                step.interval.left,
                                interval.right,
                                closed=interval_type),
                            target_location=step.target_location
                        )
                    )
                    break
                    # Interval has been completely found, useless to continue.
            else:
                raise exceptions.IntervalNotFound(interval=str(interval))
            move_sampling_list.append(
                {"action": action, "step": interval_step})

        return move_sampling_list

# Remarks: for the moment these are unused functions.


def move_convertor_permissive_into_delays(timed_automaton: TimedAutomaton,
                                          move: Move, strategy) -> List[Move]:
    """
    The function move_convertor_permissive_into_delays take a timed automaton,
    a configuration, a move and a strategy, and return if the move is
    accepted, all the possible delay_move that will be proposed to pass the
    transition, according to the (partial or complete) strategy of the
    opponent.
    :param timed_automaton:
    :param move: {"action": action, "step":  List of
                 Step(interval = interval, target_location=target_location)}
    :param strategy: the strategy function takes the interval and possible
    parameters and return the list of delay(s) that can be applied by the
    opponent.
     ------
    Example: worst_case_branch_free_opponent_strategy( guards.Interval(0,
    5) ) = [0,5]
    :return:
        """
    #
    # action = move["action"]
    # source_location = configuration.location

    if not timed_automaton.is_deterministic:
        raise exceptions.WrongTimedAutomatonClass(fct="move_convertor_permissive_into_delays",
                                                  ta_class="non-deterministic")
    # check if the target_location is indeed a successor of source_location

    return strategy(move)

    # Get the list of all the portion of the intervals
    # interval_list = []
    # for step in move["step"]:
    #     # check if the move is accepted:
    #
    #     edge = timed_automaton[source_location][step.target_location]
    #
    #     # checking if the action labels correctly the two location and if
    #     # the partial interval is accepted by the guard.
    #
    #     if action not in edge.keys() or \
    #             not edge[action].guard.guard_check_interval(configuration.valuation, step.interval):
    #         return None
    #     interval_list.append(step.interval)
    #
    # # Check if there is at least one interval
    # if len(interval_list) == 0:
    #     return None
    #
    # # Merge all intervals
    # interval = interval_list[0]
    # interval_list.remove(interval_list[0])
    # for other_interval in interval_list:
    #     interval.merge(other_interval)

    # # Get the list of delays
    #
    # delay_list = strategy(interval, **kwargs)
    #
    # # Get back the action associated with each delays...
    #
    # delay_moves = []
    #
    # for delay in delay_list:
    #     for step in move["step"]:
    #         if delay in step.interval:
    #             delay_moves.append(
    #                 {"action": action, "step": [
    #                     Step(interval=delay,
    #                          target_location=step.target_location)]}
    #             )
    # return delay_moves


def next_step_permissive(timed_automaton: TimedAutomaton, configuration: Configuration, move: Move,
                         strategy) -> List[Optional[Move]]:
    """
    The function next_step_permissive take a timed automaton,
    a configuration, a move and a strategy, and return if the move is
    accepted, the possible future configurations and the associated delays.
    :param timed_automaton:
    :param configuration:
    :param move: {"action": action, "step":  List of
                Step(interval = interval, target_location=target_location)}
    :param strategy: the strategy function takes the interval and possible
    parameters and return the list of delay(s) that can be applied by the
    opponent.
    ------
    Example: worst_case_branch_free_opponent_strategy( guards.Interval(0,
    5) ) = [0,5]: the delays can be either 0 or 5.
    :return: All the future configurations, if the permissive move is
    accepted,
    considering the complete or partial strategy of the opponent.
    """

    delays_moves = move_convertor_permissive_into_delays(
        timed_automaton, move, strategy)

    return [next_step(timed_automaton, configuration, delay_move) for
            delay_move in delays_moves]
