# coding=utf-8
"""
==================================================
Strategy module
==================================================
This module provide the strategy of the opponent in the permissive runs

Classes:
------
TODO: rename into
TODO: enumerate all classes
TODO: The interval classes come from pandas, a library for machine learning
Methods:
TODO: enumerate all methods.
------
"""
from fractions import Fraction
from typing import List, Callable, Optional

import pyrobustness.dtype
from pyrobustness.dtype import Action, Delay, Sampling_Step
import pyrobustness.runs.exceptions as exceptions
from pyrobustness.ta.interval import Interval
from pyrobustness.misc import step_range
import pyrobustness.runs.moves as moves

Move = moves.Move


def delay_move_creator(
        action: Action, delay: Delay, target_location: int) -> Move:
    """
    transforms a tuple of action, delay and integer into a Move, where the interval is a single delay
    :param action: an Action
    :param delay: an integer, fraction or math.inf
    :param target_location: an integer
    :return: a Move
    """
    pyrobustness.dtype.check_delay_type(delay)
    return {"action": action, "step": moves.Step(
        interval=delay,
        target_location=target_location)}


def create_delay_move_from_delay(move: Move) -> Callable[[Delay], Move]:
    def create_move(delay: Delay) -> Move:
        for s in move["step"]:
            if delay in s.interval:
                return {
                    "action": move["action"],
                    "step": [
                        moves.Step(interval=delay,
                                   target_location=s.target_location)
                    ]
                }

        raise exceptions.DelayNotFound(place="move's step")

    return create_move


def worst_case_branch_free_opponent_strategy() -> Callable[[Move], List[Move]]:
    """
    To be applied only on deterministic move
    Return the bound's move associated of the global interval of a move
    :param move: a Move
    :return: a list of delays's moves
    """

    def strategy(move: Move) -> List[Move]:
        interval = moves.global_interval(move)
        if interval.is_empty():
            return []
        if interval.open_left or interval.open_right:
            raise exceptions.OpenInterval(used_fct="worst_case_branch_free_opponent_strategy",
                                          interval=str(interval),
                                          right_function="worst_case_approximate_branch_free_opponent_strategy")
        return [
            {
                "action": move["action"],
                "step": [moves.Step(
                    interval=interval.left,
                    target_location=move["step"][0].target_location
                )]
            },
            {
                "action": move["action"],
                "step": [moves.Step(
                    interval=interval.right,
                    target_location=move["step"][
                        len(move["step"]) - 1].target_location
                )]
            }
        ]

    return strategy


def worst_case_approximate_branch_free_opponent_strategy(
        epsilon: Sampling_Step) -> Callable[[Move], List[Move]]:
    """
    Create from the (open left or right, or both) global interval of a move an closed interval
     (with approximation epsilon), and returns the worst_case_branch_free_opponent_strategy of the new move.
    :param move: a Move
    :param epsilon: an integer, a fraction, that represents the sampling step
    :return: a list of delays's move
    """

    def strategy(move: Move) -> List[Move]:
        if type(epsilon) is not int and type(epsilon) is not Fraction:
            raise exceptions.WrongType(element="epsilon", right_type="integer or Fraction")
        interval = moves.global_interval(move)
        if interval.is_empty():
            return []
        delays = [interval.left + epsilon, interval.right - epsilon]

        return list(map(create_delay_move_from_delay(move), delays))

    return strategy


def worst_case_brut_force_opponent_strategy(
        step: Sampling_Step) -> Callable[[Move], List[Move]]:
    """
    Sample the global interval of the move into a sample of delays (with step step) and returns the associated moves.
    :param move: a Move
    :param step: a sampling step
    :return: a list of delay's move
    """

    def strategy(move: Move) -> List[Move]:
        if type(step) is not int and type(step) is not Fraction:
            raise exceptions.WrongType(element="sampling step", right_type="integer or Fraction")

        interval = moves.global_interval(move)
        if interval.is_empty():
            return []
        if not interval.open_left and not interval.open_right:
            return [create_delay_move_from_delay(move)(delay)
                    for delay in step_range(
                    interval.left,
                    interval.right + step,
                    step=step) if delay <= interval.right]
        else:
            raise exceptions.OpenInterval(used_fct="worst_case_brut_force_opponent_strategy",
                                          interval=str(interval),
                                          right_function="worst_case_brut_force_approximate_opponent_strategy")

    return strategy


def worst_case_brut_force_approximate_opponent_strategy(
        step: Sampling_Step, epsilon: Sampling_Step) -> Callable[[Move], List[Move]]:
    """
    Create from the (open left or right, or both) global interval of a move an closed interval
     (with approximation epsilon), and returns the worst_case_brut_force_opponent_strategy of the new move.
    :param step: a sampling step for sampling the interval, type: an integer or a fraction
    :param move: a Move
    :param epsilon: an integer, a fraction, that represents the sampling step
    :return: a list of delays's move
    """
    # TODO: Fusion again with brute_force function

    def strategy(move: Move) -> List[Move]:
        if type(step) is not int \
                and type(step) is not Fraction \
                and type(epsilon) is not int \
                and type(epsilon) is not Fraction:
            raise exceptions.WrongType(element="step or epsilon", right_type="integer or Fraction")
        interval = moves.global_interval(move)
        if interval.is_empty():
            return []
        interval_approx = Interval(interval.left + epsilon,
                                   interval.right - epsilon)

        return [create_delay_move_from_delay(move)(delay)
                for delay in step_range(
                interval_approx.left,
                interval_approx.right + step,
                step=step) if delay <= interval_approx.right]

    return strategy


def low_case_opponent_strategy() -> Callable[[Move], List[Move]]:
    """
    To be applied only on deterministic move
    Return the left bound's move associated of the global interval of a move
    :param move: a Move
    :return: a list of delays's moves
    """

    def strategy(move: Move) -> List[Move]:
        interval = moves.global_interval(move)
        if interval.is_empty():
            return []
        if interval.open_left:
            raise exceptions.OpenInterval(used_fct="low_case_opponent_strategy",
                                          interval=str(interval),
                                          right_function="worst_case_approximate_branch_free_opponent_strategy")
        return [{
            "action": move["action"],
            "step": [moves.Step(
                interval=interval.left,
                target_location=move["step"][0].target_location)]
        }]

    return strategy


def up_case_opponent_strategy() -> Callable[[Move], List[Move]]:
    """
    To be applied only on deterministic move
    Return the left bound's move associated of the global interval of a move
    :param move: a Move
    :return: a list of delays's moves
    """

    def strategy(move: Move) -> List[Move]:
        interval = moves.global_interval(move)
        if interval.is_empty():
            return []
        if interval.open_right:
            raise exceptions.OpenInterval(used_fct="up_case_opponent_strategy",
                                          interval=str(interval),
                                          right_function="worst_case_approximate_branch_free_opponent_strategy")
        return [{
            "action": move["action"],
            "step": [moves.Step(
                interval=interval.right,
                target_location=move["step"][
                    len(move["step"]) - 1].target_location)]
        }]

    return strategy

# noinspection PyUnusedLocal
# def worst_case_random_opponent_strategy(move: Move, **kwargs) -> List[Move]:
#     """
#
#     :param move:
#     :return: a list containing a delay sampled uniformly random among the
#     interval
#     """
#     interval = runs.global_interval(move)
#     return [create_delay_move_from_delay(move)(
#                 uniform(interval.left, interval.right))]
