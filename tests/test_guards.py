# coding=utf-8
from fractions import Fraction

from tests.test_guards_examples import *
from pyrobustness.ta.guards import AbstractConstraint, \
    LinearConstraint, LinearGuard
from pyrobustness.ta.interval import Interval
from pyrobustness.ta.exceptions import AbstractConstructionException, \
    NegativeIntervalException, NegativeClockIndexException, EmptyInterval
import math


class TestInterval:
    def test_init_non_negative_intervals(self):
        with pytest.raises(NegativeIntervalException):
            Interval(-1, 5)
        with pytest.raises(Exception):
            Interval(1, -1)

    def test_is_disjoint_and_mergeable(self, closed_interval_0_4, left_closed_interval_0_4, right_closed_interval_0_4,
                                       open_interval_0_4):
        assert open_interval_0_4.is_disjoint_and_mergeable(Interval(4, 6, closed='both'))
        assert closed_interval_0_4.is_disjoint_and_mergeable(Interval(4, 8, closed='both')) is False
        assert open_interval_0_4.is_disjoint_and_mergeable(Interval(4, 8, closed='neither')) is False
        assert closed_interval_0_4.is_disjoint_and_mergeable(Interval(4, 8, closed='both')) is False

    def test_merge(self, closed_interval_0_4, left_closed_interval_0_4, right_closed_interval_0_4,
                   open_interval_0_4, closed_interval_4_6, left_closed_interval_4_6, right_closed_interval_4_6,
                   open_interval_4_6):
        # Test with mergeable intervals:

        assert open_interval_0_4.merge(closed_interval_4_6) == Interval(0, 6, closed='right')
        assert open_interval_0_4.merge(left_closed_interval_4_6) == Interval(0, 6, closed='neither')
        assert right_closed_interval_0_4.merge(right_closed_interval_4_6) == Interval(0, 6, closed='right')
        assert right_closed_interval_0_4.merge(right_closed_interval_4_6) == Interval(0, 6, closed='right')
        assert left_closed_interval_0_4.merge(closed_interval_4_6) == Interval(0, 6, closed='both')
        assert left_closed_interval_0_4.merge(left_closed_interval_4_6) == Interval(0, 6, closed='left')

        # Test with non continuous intervals:
        with pytest.raises(Exception):
            Interval(0, 4, closed='neither').merge(Interval(4, 6, closed='neither'))

        with pytest.raises(Exception):
            Interval(0, 3, closed='both').merge(Interval(4, 6, closed='neither'))

        # Test with non disjoint intervals:
        with pytest.raises(Exception):
            Interval(0, 4, closed='both').merge(Interval(4, 6, closed='both'))
        with pytest.raises(Exception):
            Interval(0, 4, closed='both').merge(Interval(4, 6, closed='left'))
        with pytest.raises(Exception):
            Interval(0, 4, closed='right').merge(Interval(4, 6, closed='left'))
        with pytest.raises(Exception):
            Interval(0, 4, closed='right').merge(Interval(4, 6, closed='both'))

    def test_sub_interval(self, closed_interval_0_4, left_closed_interval_0_4, right_closed_interval_0_4,
                          open_interval_0_4, closed_interval_4_6):
        # Test with closed intervals and correct subbounds
        assert closed_interval_0_4.sub_interval(0, 3) == Interval(0, 3, closed='both')
        assert closed_interval_0_4.sub_interval(0, 4) == Interval(0, 4, closed='both')
        assert closed_interval_0_4.sub_interval(1, 3) == Interval(1, 3, closed='both')

        # Test with right closed interval and correct subbounds

        assert right_closed_interval_0_4.sub_interval(0, 3) == Interval(0, 3, closed='right')
        assert right_closed_interval_0_4.sub_interval(0, 4) == Interval(0, 4, closed='right')
        assert right_closed_interval_0_4.sub_interval(1, 3) == Interval(1, 3, closed='both')

        # Test with left closed interval and correct subbounds

        assert left_closed_interval_0_4.sub_interval(0, 3) == Interval(0, 3, closed='both')
        assert left_closed_interval_0_4.sub_interval(0, 4) == Interval(0, 4, closed='left')
        assert left_closed_interval_0_4.sub_interval(1, 4) == Interval(1, 4, closed='left')
        assert left_closed_interval_0_4.sub_interval(1, 3) == Interval(1, 3, closed='both')

        # Test with open interval and correct subbounds

        assert open_interval_0_4.sub_interval(0, 3) == Interval(0, 3, closed='right')
        assert open_interval_0_4.sub_interval(0, 4) == Interval(0, 4, closed='neither')
        assert open_interval_0_4.sub_interval(1, 4) == Interval(1, 4, closed='left')
        assert open_interval_0_4.sub_interval(1, 3) == Interval(1, 3, closed='both')

        # Test with non included subintervals:

        with pytest.raises(Exception):
            assert closed_interval_4_6.sub_interval(0, 2)
        with pytest.raises(Exception):
            assert closed_interval_4_6.sub_interval(2, 6)
        with pytest.raises(Exception):
            assert closed_interval_4_6.sub_interval(5, 8)

    def test_semi_sorted_sampling(self, closed_interval_4_6, left_closed_interval_0_4, right_closed_interval_0_4,
                                  open_interval_0_4, infinite_interval_4_inf):
        sampling_4_6_1 = [Interval(4, 6, closed='both'), Interval(4, 5, closed='both'),
                          Interval(5, 6, closed='both')]
        assert closed_interval_4_6.semi_sorted_sampling(1) == sampling_4_6_1

        sampling_0_4_1_left = [Interval(0, 4, closed='left'), Interval(0, 3, closed='both'),
                               Interval(0, 2, closed='both'), Interval(0, 1, closed='both'),
                               Interval(1, 3, closed='both'), Interval(1, 2, closed='both'),
                               Interval(2, 3, closed='both'), Interval(1, 4, closed='left'),
                               Interval(2, 4, closed='left'), Interval(3, 4, closed='left')]
        assert left_closed_interval_0_4.semi_sorted_sampling(1) == sampling_0_4_1_left

        sampling_0_4_1_right = [Interval(0, 4, closed='right'), Interval(0, 3, closed='right'),
                                Interval(0, 2, closed='right'), Interval(0, 1, closed='right'),
                                Interval(1, 3, closed='both'), Interval(1, 2, closed='both'),
                                Interval(2, 3, closed='both'), Interval(1, 4, closed='both'),
                                Interval(2, 4, closed='both'), Interval(3, 4, closed='both')]
        assert right_closed_interval_0_4.semi_sorted_sampling(1) == sampling_0_4_1_right

        sampling_0_4_1_open = [Interval(0, 4, closed='neither'), Interval(0, 3, closed='right'),
                               Interval(0, 2, closed='right'), Interval(0, 1, closed='right'),
                               Interval(1, 3, closed='both'), Interval(1, 2, closed='both'),
                               Interval(2, 3, closed='both'), Interval(1, 4, closed='left'),
                               Interval(2, 4, closed='left'), Interval(3, 4, closed='left')]
        assert open_interval_0_4.semi_sorted_sampling(1) == sampling_0_4_1_open

        sampling_4_6_1 = [Interval(4, 6, closed='both'), Interval(4, 5, closed='both'),
                          Interval(5, 6, closed='both')]
        assert infinite_interval_4_inf.semi_sorted_sampling(step=1, bound=6) == sampling_4_6_1

    def test_init_non_inverted_bounds(self):
        with pytest.raises(Exception):
            Interval(2, 1)

    def test_bounds(self):
        assert Interval(0, 5).left == 0
        assert Interval(0, 5).right == 5


class TestAbstractConstraint:
    def test_init(self):
        with pytest.raises(AbstractConstructionException):
            AbstractConstraint()


class TestLinearConstraint:
    def test_init(self, linear_constraint_standard,
                  linear_constraint_infinite_bounds):
        assert linear_constraint_standard.interval == Interval(0, 1)
        assert linear_constraint_standard.clock_index == 0

        assert linear_constraint_infinite_bounds.interval == Interval(0, inf)
        assert linear_constraint_infinite_bounds.clock_index == 1

        with pytest.raises(NegativeIntervalException):
            linear_constraint_negative_bounds()

        with pytest.raises(NegativeClockIndexException):
            linear_constraint_negative_clock_index()

    def test_eq(self, linear_constraint_standard,
                linear_constraint_standard_clone,
                linear_constraint_standard_not_clone):
        """
        Role of the tests: test if the function __eq__ works well. We take
        one constraint, have a clone and a modified constraint, and compare.
        :param linear_constraint_standard: a linear constraint
        :param linear_constraint_standard_clone: a clone of it.
        :param linear_constraint_standard_not_clone: a modified constraint
        """
        assert linear_constraint_standard == linear_constraint_standard_clone
        assert linear_constraint_standard != \
               linear_constraint_standard_not_clone

    def test_constraint_check(self, linear_constraint_standard,
                              linear_constraint_infinite_bounds):
        """
        Test with different valuations and delays the function
        constraint_check.
        :param linear_constraint_standard: a standard bounded constraint
        :param linear_constraint_infinite_bounds: a standard unbounded
        constraint. Should verify every positive delay, for every positive
        valuation.
        """
        pass

    def test_enabled_delay_set(self, linear_constraint_standard,
                               linear_constraint_infinite_bounds,
                               linear_constraint_standard_third_clock):
        """
        Test with different valuations and delays the function
        enabled_delay_set
        :param linear_constraint_standard: a standard bounded constraint.
        :param linear_constraint_infinite_bounds: a standard unbounded
        constraint. should return [0, inf]
        """

        assert linear_constraint_standard.enabled_delays_set([0, 4]) == \
               Interval(0, 1)

        assert linear_constraint_standard.enabled_delays_set([Fraction(3, 10), 20]) == \
               Interval(0, Fraction(7, 10))

        assert linear_constraint_standard.enabled_delays_set([1, 3]) == \
               Interval(0, 0)

        with pytest.raises(EmptyInterval):
            linear_constraint_standard.enabled_delays_set([Fraction(11, 10), 3])

        assert linear_constraint_infinite_bounds.enabled_delays_set([0, 4]) == \
               Interval(0, math.inf)

        assert linear_constraint_standard_third_clock.enabled_delays_set(
            [5, 6, 1, 2]) == Interval(9, 28)

        assert linear_constraint_standard_third_clock.enabled_delays_set(
            [5, 6, 1, 11]) == Interval(0, 19)


class TestAbstractGuard:
    pass


# TODO: Checker guard_check et guard_check_interval, valuation_after_passing_guard, enabled_delays_set and disjoint:
#  these are the most used function!


class TestLinearGuard:

    def test_guard_check(self, standard_linear_guard):
        assert standard_linear_guard.guard_check([0, 0], Fraction(1, 5))
        assert standard_linear_guard.enabled_delays_set([0, 0]) == Interval(0, 3)


# TODO :test equality


class TestLabel:
    def test_label(self, standard_linear_label, standard_linear_guard):
        assert standard_linear_label.guard == standard_linear_guard

        assert standard_linear_label.guard.guard_check([0, 0], Fraction(1, 5))


# TODO: recup these tests to label test


class TestTransition:

    def test_init(self, transition_empty_reset, transition_1, transition_2):
        assert transition_empty_reset.data["a"].guard == LinearGuard([
            LinearConstraint(clock_index=0, lower_bound=0, upper_bound=1)
        ])
        assert transition_empty_reset.data["a"].resets == []

        # Multiple guards
        assert transition_1.data["b"].guard == LinearGuard([
            LinearConstraint(clock_index=0, lower_bound=0, upper_bound=1),
            LinearConstraint(clock_index=1, lower_bound=2, upper_bound=3)
        ])
        assert transition_1.data["b"].resets == [1]

        # Unbounded constraints
        assert transition_2.data["c"].guard == LinearGuard([
            LinearConstraint(clock_index=0, lower_bound=0, upper_bound=+inf),
        ])
        assert transition_2.data["c"].resets == []
