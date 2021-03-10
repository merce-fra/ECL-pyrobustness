# coding=utf-8
"""
==================================================
Guards module
==================================================
This module provide the guard representation. The goal is to provide a
general tool for general constraints and to differentiate the objects by the
type of constrains they have (diagonal constraints, linear constraints...)

Classes:
AbstractConstraint: provides an abstract objet to represent general constraint
linearConstraint: provides an particular type of constraint: the linear
constraint.

AbstractGuard:  provides an abstract objet to represent general guards.
Guard in general are objects that contain a list of constraints.
LinearGuard: provide guard that contain only linear constrains.

Transition: provide an object that represents the transitions: a couple of
guards and a set of resets.

------
"""
from __future__ import annotations  # For forward reference typing

import pyrobustness.ta.exceptions as exceptions
from pyrobustness.dtype import Delay, Valuation, Reset, check_delay_type
from pyrobustness.ta.interval import Interval
from typing import List


class AbstractConstraint(object):  # pragma: no cover
    def __init__(self):
        raise exceptions.AbstractConstructionException

    def constraint_check(self, valuation, delay) -> bool:
        return False

    def __eq__(self, other) -> bool:
        return False


class LinearConstraint(AbstractConstraint):
    __slots__ = ["interval", "clock_index"]

    # noinspection PyMissingConstructor
    def __init__(self, lower_bound, upper_bound, clock_index):
        # TODO: Document that intervals are considered as closed.
        self.interval = Interval(lower_bound, upper_bound)
        if clock_index < 0:
            raise exceptions.NegativeClockIndexException
        self.clock_index = clock_index

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        s = [str(self.interval.left) + ' =< x_' +
             str(self.clock_index) +
             ' =< ' + str(self.interval.right) + "\n"]
        return ' '.join(s)

    def __eq__(self, other) -> bool:
        return self.interval == other.interval \
               and self.clock_index == other.clock_index

    def constraint_check(self, valuation: Valuation, delay: Delay) -> bool:
        """
        returns a bool that is True if and only if the vector valuation + delay checks the constraint.
        :param valuation: array_like of integer, fraction or math.inf
        :param delay: an integer, a fraction, or math.inf
        :return: a bool
        """
        check_delay_type(delay)
        for val in valuation:
            check_delay_type(val)

        applied_valuation = valuation[self.clock_index] + delay
        return applied_valuation in self.interval

    def constraint_check_interval(self, valuation: Valuation, interval: Interval) -> bool:
        """
        returns a cool that is True if and only if the vector valuation + interval checks the constraint
        :param valuation: array-like of integer, fraction or math.inf
        :param interval: an interval
        :return: a bool
        """
        for val in valuation:
            check_delay_type(val)

        interval_valuation = Interval(
            interval.left + valuation[self.clock_index],
            interval.right + valuation[self.clock_index],
            closed=interval.closed)

        return self.interval.include(interval_valuation)

    def enabled_delays_set(self, valuation: Valuation) -> Interval:
        """
        returns an interval that represents all the delays that are enable for this constraint
        :param valuation: array_like
        :return: an Interval.
        """
        lower_bound = max(0, self.interval.left - valuation[self.clock_index])
        upper_bound = self.interval.right - valuation[self.clock_index]

        if upper_bound < lower_bound:
            raise exceptions.EmptyInterval
        else:
            return Interval(lower_bound, upper_bound)


class AbstractGuard(object):
    def __init__(self, constraints):
        if len(list(constraints)) == 0:
            raise exceptions.ConstraintNotFoundException
        self.constraints = list(constraints)

    def __len__(self):
        """
        return the length of the guards (i.e the number of constraints)
        :return: an integer
        """
        return len(self.constraints)

    def add_constraints(self, constraints: List[AbstractConstraint]):
        """
        add constraints to the guard
        :param constraints: a list of constraints
        """
        self.constraints.extend(constraints)

    def guard_check(self, valuation: Valuation, delay: Delay) -> bool:
        """
        returns a bool that is True if and only if the vector valuation + delay checks the guard.
        :param valuation: array_like of int, faction, or math.inf
        :param delay: an integer, a fraction, or math.inf
        :return: a bool
        """

        # checking the type
        check_delay_type(delay)
        for val in valuation:
            check_delay_type(val)

        # checking the guard
        for constraint in self.constraints:
            if not constraint.constraint_check(valuation, delay):
                return False
        return True

    def guard_check_interval(self, valuation: Valuation, interval: Interval):
        """
        returns a bool that is True if and only if the vector valuation + interval checks the guard.
        :param valuation: array_like of int, faction, or math.inf
        :param interval: an interval
        :return: a bool
        """
        # checking the type
        for val in valuation:
            check_delay_type(val)

        # checking the guard
        for constraint in self.constraints:
            if not constraint.constraint_check_interval(valuation, interval):
                return False
        return True

    def valuation_after_passing_guard(self, valuation: Valuation, delay: Delay) -> Valuation:
        """
        WARNING: This does not take resets into account
        returns the valuation applied after passing the guard, and BEFORE applying any resets
        :param valuation: array_like of int, faction, or math.inf
        :param delay: an integer, faction, or math.inf
        :return: a valuation
        """

        # checking the type
        for val in valuation:
            check_delay_type(val)
        check_delay_type(delay)

        if self.guard_check(valuation, delay):
            return [valuation[i] + delay for i in valuation]

    def enabled_delays_set(self, valuation: Valuation) -> Interval:  # pragma: no cover
        raise exceptions.AbstractConstructionException("AbstractGuard")

    def well_formed(self, nb_clock: int) -> bool:  # pragma: no cover
        raise exceptions.AbstractConstructionException("AbstractGuard")

    def __eq__(self, other: AbstractGuard) -> bool:
        # Warning: The well-behavior of this function depends in the indexation
        # of the guards and resets.
        return self.constraints == other.constraints

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __str__(self) -> str:  # pragma: no cover
        s = ["Guard:\n"]
        s += [str(constraint) for constraint in self.constraints]
        return ''.join(s)


class LinearGuard(AbstractGuard):

    # TODO: add something to deal with someone adding two constraints with
    #  same clock_index. Sol1: exception and raise an error. Sol2: merge
    #  every constraints...
    # With DBM = no pb.

    def enabled_delays_set(self, valuation: Valuation) -> Interval:
        """
        returns an interval that represents all the delays that are enable for this linear guard
        :param valuation: array_like
        :return: an Interval.
        """

        for val in valuation:
            check_delay_type(val)

        # all interval are of the form [a,b] with a, b >= 0 and a < b
        # The cap of all [a,b] is
        try:
            intervals = [g.enabled_delays_set(valuation) for g in
                         self.constraints]

            lb = max([i.left for i in intervals])
            ub = min([i.right for i in intervals])

            if lb > ub:
                return Interval(0, 0, closed='neither')
            # Raise exception when empty, or [3,2]
            # Enable to generalize to abstract guard if the enabled_delay_set
            # for each constraint is of the form: | x, y | with x,y float. Ask
            # Nico. Ex: still OK for 0 =< x+y-z =< 5?
            # check if cap int is enabled in pandas
            # Nico: contrainte diagonale x-y , x-z, etc: OK
            # Nico: contrainte affine: une horloge OK, mais x+b*y bof?
            # Nico: 3 horloge: non!
            else:
                return Interval(lb, ub)

        except exceptions.EmptyInterval:
            return Interval(0, 0, closed='neither')

    def well_formed(self, nb_clock: int) -> bool:
        for constraint in self.constraints:
            if constraint.clock_index > nb_clock - 1 or \
                    constraint.clock_index < 0:
                raise exceptions.IndexOutOfRange(constraint, "clock")
            if constraint.interval.left < 0 or constraint.interval.right < 0:
                raise exceptions.NegativeIntervalException

        return True

    def disjoint(self, other_guard: LinearGuard) -> bool:
        """
        returns True if other is disjoint with self
        :param other_guard: a LinearGuard
        :return: a bool
        """
        """
        Check if two linear guards are disjoint or not.
        :param other_guard:
        :return:
        """
        for constraint in self.constraints:
            clock = constraint.clock_index
            interval = constraint.interval
            for other_constraint in other_guard.constraints:
                if other_constraint.clock_index == clock:
                    if other_constraint.interval.overlaps(interval):
                        return False

        return True


class Label(object):
    """
    Label(object)

    Convert a list of couple of integer and a list of integer into a
    transition. The first list [g_0,...,g_n] of couple of integer
    represents, for each element g_i=[l_i, u_i] the lower (l_i) and
    upper (u_i) bound for the i-th clock. The second list [r_i]_{i in R}
    represents of index of clocks that will be reset after the transition.

    :parameter
    ----------

    guards: an array of namedtuple of the form "clock_index", "lower_bound"
    and "upper bound".
    resets: 1-D array of integers [r_i]_i. The length of the lists
    correspond of the number of clocks that are reset.

    :returns:
    ----------

    guards: an array of collection, that gives the clock index, the lower
    bound and the upper bound of each guard.
    resets: an 1-D array of integers that represent the index of clocks that
    are reset in the transition.

    Examples
    ----------

    """

    def __init__(self, guard: AbstractGuard, resets: Reset):

        if len(guard) == 0:
            raise exceptions.GuardNotFoundException
        self.guard = guard
        self.resets = list(sorted(resets))

    def well_formed(self, nb_clocks: int):
        if len(self.resets) != 0 and \
                (max(self.resets) > nb_clocks or min(self.resets) < 0):
            raise exceptions.IndexOutOfRange(max(self.resets), "reset")

        return self.guard.well_formed(nb_clocks)

    def __eq__(self, other: Label) -> bool:
        # Warning: The well-behavior of this function depends in the indexation
        # of the guards and resets.
        if self.guard != other.guard:
            return False
        if self.resets != other.resets:
            return False
        return True

    def __repr__(self) -> str:  # pragma: no cover
        return self.__str__()

    def __str__(self) -> str:  # pragma: no cover
        s = [str(self.guard)]
        s += ["Resets:\n"]
        s += ["x_" + str(r) for r in self.resets]

        return ' '.join(s)
