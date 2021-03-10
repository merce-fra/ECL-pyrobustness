# coding=utf-8
from fractions import Fraction

import pytest

import pyrobustness.runs.opponentstrategy as opponent_strategy
import pyrobustness.runs.moves as moves
from tests.test_opponentstrategy_examples import *
import pyrobustness.runs.exceptions as exceptions
import math


def mock_move(interval):
    return {
        "action": "a",
        "step": [moves.Step(interval=interval, target_location=0)]
    }


class TestWorstCaseStrategy:

    def test_worst_case_branch_free_opponent_strategy(
            self, interval_positive_closed, interval_positive_infinite_closed,
            interval_positive_open_left, interval_positive_open_right,
            interval_positive_open_both):
        """
        Unitary tests about the function
        worst_case_branch_free_opponent_strategy

        :param interval_positive_closed: an interval [0,5]
        :param interval_positive_infinite_closed: an interval [0, +inf]
        :param interval_positive_open_left: an interval (0,5]
        :param interval_positive_open_right: an interval [0,5)
        :param interval_positive_open_both: an interval (0,5)
        :return: Test if:
        1) for closed interval, if the test well return the list of bounds
        of the interval
        2) for open intervals (left, right or both), if the test well
        returns that the function raises an exception: we cannot return the
        exact bounds of an open interval. An approximation function should
        be called instead.
        """

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_branch_free_opponent_strategy()(
                            mock_move(interval_positive_closed)))) == [0, 5]

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_branch_free_opponent_strategy()(
                            mock_move(interval_positive_infinite_closed)))) == \
               [0, math.inf]

        # Verify that this function fails when the intervals are open one at
        # least one side
        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.worst_case_branch_free_opponent_strategy()(
                mock_move(interval_positive_open_left))

        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.worst_case_branch_free_opponent_strategy()(
                mock_move(interval_positive_open_right))

        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.worst_case_branch_free_opponent_strategy()(
                mock_move(interval_positive_open_both))

    def test_worst_case_branch_free_approximate_opponent_strategy(
            self, interval_positive_closed, interval_positive_open_both):
        """
        Unitary tests about an approximate function of
        worst_case_branch_free_opponent_strategy. Its role is to return the
        approximate bounds of the interval |a,b|, with a step e. Its should
        return {a+e, b-e}, if a+e < b-e.
        :param interval_positive_closed: Interval [0,5]
        :param interval_positive_open_both: Interval (0,5)
        :return: The tests verify if the approximate bounds are corrects,
        then verify that the functions raises an error if a overatted step
        is proposed.
        """

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_approximate_branch_free_opponent_strategy(
                            Fraction(1, 2))(mock_move(interval_positive_closed)))) == [Fraction(1, 2), Fraction(9, 2)]

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_approximate_branch_free_opponent_strategy(1)
                        (mock_move(interval_positive_open_both)))) == [1, 4]

        with pytest.raises(Exception):
            strat = opponent_strategy.worst_case_approximate_branch_free_opponent_strategy(Fraction(51, 10))
            strat(mock_move(interval_positive_closed))

        with pytest.raises(Exception):
            strat = opponent_strategy.worst_case_approximate_branch_free_opponent_strategy(Fraction(501, 100))
            strat(mock_move(interval_positive_open_both))


class TestBruteForceStrategy:
    def test_worst_case_brut_force_opponent_strategy(
            self, interval_positive_closed, interval_float_bounds,
            interval_positive_infinite_closed):
        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_brut_force_opponent_strategy(2)
                        (mock_move(interval_positive_closed))
                        )) == [0, 2, 4]
        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_brut_force_opponent_strategy(1000)
                        (mock_move(interval_positive_closed))
                        )) == [0]
        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.worst_case_brut_force_opponent_strategy(4)(mock_move(interval_float_bounds))
                        )) == [0]

        with pytest.raises(ValueError):
            opponent_strategy.worst_case_brut_force_opponent_strategy(2)(mock_move(interval_positive_infinite_closed))
            # TODO: make my own exception to ask the user to fill a
            #  non-infinite interval


class TestSingleDelayStrategy:
    def test_low_case_opponent_strategy(
            self, interval_positive_closed, interval_positive_infinite_closed,
            interval_positive_open_left, interval_positive_open_right,
            interval_positive_open_both):
        """
        Unitary tests about the function
        low_case_opponent_strategy

        :param interval_positive_closed: an interval [0,5]
        :param interval_positive_infinite_closed: an interval [0, +inf]
        :param interval_positive_open_left: an interval (0,5]
        :param interval_positive_open_right: an interval [0,5)
        :param interval_positive_open_both: an interval (0,5)
        :return: Test if:
        1) for closed interval, if the test well return the list of bound
        of the interval
        2) for open intervals (left, right or both), if the test well
        returns that the function raises an exception: we cannot return the
        exact bounds of an open interval. An approximation function should
        be called instead.
        """

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.low_case_opponent_strategy()(
                            mock_move(interval_positive_closed)))) == [0]

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.low_case_opponent_strategy()(
                            mock_move(interval_positive_infinite_closed)))) == [0]

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.low_case_opponent_strategy()(
                            mock_move(interval_positive_open_right)))) == [0]

        # Verify that this function fails when the intervals are open one at
        # least one side
        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.low_case_opponent_strategy()(mock_move(
                interval_positive_open_left))

        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.low_case_opponent_strategy()(mock_move(
                interval_positive_open_both))

    def test_up_case_opponent_strategy(
            self, interval_positive_closed, interval_positive_infinite_closed,
            interval_positive_open_left, interval_positive_open_right,
            interval_positive_open_both):
        """
        Unitary tests about the function
        low_case_opponent_strategy

        :param interval_positive_closed: an interval [0,5]
        :param interval_positive_infinite_closed: an interval [0, +inf]
        :param interval_positive_open_left: an interval (0,5]
        :param interval_positive_open_right: an interval [0,5)
        :param interval_positive_open_both: an interval (0,5)
        :return: Test if:
        1) for closed interval, if the test well return the list of bound
        of the interval
        2) for open intervals (left, right or both), if the test well
        returns that the function raises an exception: we cannot return the
        exact bounds of an open interval. An approximation function should
        be called instead.
        """

        assert list(map(lambda d: d["step"][0].interval, opponent_strategy.up_case_opponent_strategy()(
            mock_move(interval_positive_closed)))) == [5]

        assert list(map(lambda d: d["step"][0].interval, opponent_strategy.up_case_opponent_strategy()(
            mock_move(interval_positive_infinite_closed)))) == [math.inf]

        assert list(map(lambda d: d["step"][0].interval,
                        opponent_strategy.up_case_opponent_strategy()(
                            mock_move(interval_positive_open_left)))) == [5]

        # Verify that this function fails when the intervals are open one at
        # least one side
        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.up_case_opponent_strategy()(mock_move(
                interval_positive_open_right))

        with pytest.raises(exceptions.OpenInterval):
            opponent_strategy.up_case_opponent_strategy()(mock_move(
                interval_positive_open_both))


class TestRandomStrategy:
    def test_worst_case_random_opponent_strategy(self):
        pass
    # TODO: LATER...
