# coding=utf-8
from __future__ import annotations  # For forward reference typing
import math
from fractions import Fraction
from operator import gt, ge, lt, le
from typing import Union, Optional

from pyrobustness.misc import step_range
from pyrobustness.ta import exceptions as exceptions
from pyrobustness.dtype import Delay, check_delay_type


class Interval(object):
    def __init__(self, lower_bound: Delay, upper_bound: Delay, closed: str = "both"):

        if lower_bound < 0:
            raise exceptions.NegativeIntervalException
        if lower_bound > upper_bound:
            raise exceptions.BoundException(lower_bound=str(lower_bound),
                                            upper_bound=str(upper_bound))

        if type(lower_bound) == int:
            lower_bound = Fraction(lower_bound, 1)
        elif type(lower_bound) != Fraction and not math.isinf(lower_bound):
            raise exceptions.WrongType(element="lower bound=" + str(lower_bound),
                                       right_type="integer or Fraction, or math.inf")
        if type(upper_bound) == int:
            upper_bound = Fraction(upper_bound, 1)
        elif type(upper_bound) != Fraction and not math.isinf(upper_bound):
            raise exceptions.WrongType(element="upper_bound=" + str(upper_bound),
                                       right_type="integer or Fraction, or math.inf")

        self.left = lower_bound
        self.right = upper_bound
        if closed not in ['both', 'right', 'left', 'neither']:
            raise exceptions.IllegalClosedArgument
        self.closed = closed

    @property
    def closed_right(self) -> bool:
        """
        Is defined as a getter function!
        returns True if the interval is closed at the right side
        :return: a bool
        """
        return self.closed in ["both", "right"]

    @property
    def open_right(self) -> bool:
        """
        Is defined as a getter function!
        returns True if the interval is open at the right side
        :return: a bool
        """
        return not self.closed_right

    @property
    def closed_left(self) -> bool:
        """
        Is defined as a getter function!
        returns True if the interval is closed at the left side
        :return: a bool
        """
        return self.closed in ["both", "left"]

    @property
    def open_left(self) -> bool:
        """
        Is defined as a getter function!
        returns True if the interval is open at the left side
        :return: a bool
        """
        return not self.closed_left

    def size(self) -> Union[Fraction, int, float]:
        """
        return the length of an interval
        :return: a Fraction
        """
        if math.isinf(self.right):
            return math.inf
        if math.isinf(self.left):
            raise Exception
        return self.right - self.left

    def __lt__(self, other: Interval) -> bool:
        """
        checks if self is strictly less than other
        :param other: an Interval
        :return: bool
        """
        return (self.left < other.left) or ((self.left == other.left) and (self.right < other.right))

    def __eq__(self, other: Interval) -> bool:
        return (self.left == other.left) and (self.right == other.right)

    def __le__(self, other: Interval) -> bool:
        """
        checks if self is less than or equal to other
        :param other: an Interval
        :return: a bool
        """
        return (self == other) or (self < other)

    def __contains__(self, item: Delay) -> bool:
        """
        checks if self contains the item
        :param item: a delay
        :return: a bool
        """
        check_delay_type(item)
        op1 = gt if self.open_left else ge
        op2 = lt if self.open_right else le

        return op1(item, self.left) and op2(item, self.right)

    def __str__(self) -> str:
        left_repr = "[" if self.closed_left else "("
        right_repr = "]" if self.closed_right else ")"
        return left_repr + str(self.left) + ", " + str(self.right) + right_repr

    def __repr__(self) -> str:
        return self.__str__()

    def is_empty(self):
        """
        checks if self is an empty interval (i.e does not contains any delay)
        :return: a bool
        """
        return (self.right == self.left) & (self.closed != 'both')

    def overlaps(self, other: Interval) -> bool:
        """
        checks self and other overlaps
        :param other: an Interval
        :return: a bool
        """

        if type(other) != Interval:
            raise exceptions.WrongType(element="other=" + str(other),
                                       right_type="Interval")

        op1 = le if (self.closed_left and other.closed_right) else lt
        op2 = le if (other.closed_left and self.closed_right) else lt

        return op1(self.left, other.right) & op2(other.left, self.right)

    def is_disjoint_and_mergeable(self, other: Interval) -> bool:
        """ Check if two intervals are mergeable.
            Example:
                [0,2] and [2,5] are mergeable into [0,5]
                [0,2[ and [2,5] can be merged into [0,5]
                but [0,2[ and ]2,5] cannot be merged.
                and [0,6] and [4,8] cannot be merged."""

        lowest, highest = (self, other) if self.left < other.left else \
            (other, self)

        return highest.left == lowest.right and \
               (highest.closed_left or lowest.closed_right) and \
               not self.overlaps(other)

    def include(self, other: Interval) -> bool:
        """ check if self includes other"""
        if self.closed == 'both':
            return self.left in other and self.right in other

        elif self.closed == 'right':
            return self.left >= other.left and self.right in other

        elif self.closed == 'left':
            return other.right >= self.right and self.left in other

        elif self.closed == 'neither':
            return self.left >= other.left and self.right <= other.right

    @staticmethod
    def interval_type(left: bool, right: bool) -> str:
        """
        :param left: bool that values True if (and only if) the lowest interval is left closed
        :param right: bool that values True if (and only if) the highest interval is right closed
        :return:
        """
        if left and right:
            return 'both'
        elif left and not right:
            return 'left'
        elif not left and not right:
            return 'neither'
        else:
            return 'right'

    def merge(self, other: Interval) -> Interval:
        """
        merge two intervals, if and only if they are disjoint and concatenable.
        :param other: an Interval
        :return: an Interval
        Example:
        [2,3], (3,5] will merge into [2,5]
        but [2,3] and [3,5] will not merge, because they overlaps.
        (2,3) and (4,5) will not merge, because they are not concatenable.
        """
        lowest, highest = (self, other) if self.left < other.left else (other, self)
        if not self.is_disjoint_and_mergeable(other):
            raise exceptions.NotMergeableOrDisjointIntervals(int_1 = self, int_2=other)

        closed_type = self.interval_type(lowest.closed_left,
                                         highest.closed_right)
        return Interval(lowest.left, highest.right, closed=closed_type)

    def sub_interval(self, left: Delay, right: Delay) -> Interval:
        """
        This function create an subinterval of self, such that it conserves
        self's open attributes: If self = (0,5], the subinterval(0,3) will
        be (0,3], but the subinterval (1,3) will be [1,3]
        :param left: the left bound of the subinterval
        :param right: the right bound of the subinterval
        :return: an interval
        """
        if left < self.left or right > self.right:
            raise exceptions.NotIncludedInterval(int_1=str([left, right]),
                                                 int_2=str(self)
                                                 )
        if left == self.left and right == self.right:
            return Interval(left, right, closed=self.closed)

        elif left == self.left and right != self.right \
                and self.closed in ['right', 'neither']:
            return Interval(left, right, closed='right')

        elif left != self.left and right == self.right \
                and self.closed in ['left', 'neither']:
            return Interval(left, right, closed='left')

        else:
            return Interval(left, right, closed='both')

    def semi_sorted_sampling(self, step: Union[int, Fraction], bound: Optional[Union[int, Fraction]] = None):
        """
        This function return a finite list of possible interval contained
        in an interval, with a step k. For instance if we apply [0,
        1].sampling(0.5) it return [[0, 0.5], [0, 1], [0.5, 1]].

        WARNING: THIS FUNCTION IS SORTED such that:
        1) the first interval is the greatest one.
        2) then the firsts intervals are all the intervals I
        such that I.left = self.left
        3) then the lasts interval are all the intervals I such that
        I.right = self.right (except self)
        :param step: an integer
        :param bound: a bound to truncate infinite interval into finite, closed at right, interval
        :return: a list of intervals
        """

        # Dealing with infinite intervals
        sleft = self.left
        # sright = bound + self.left + step if (bound is not None and math.isinf(self.right)) else self.right
        sright = bound if (bound is not None and math.isinf(self.right)) else self.right
        sampling = [Interval(sleft, sright, closed=self.closed)]

        for left in step_range(sleft, sright + step, step):
            for right in step_range(sright - step, left, - step):
                sampling.append(self.sub_interval(left, right))

        for left in step_range(sleft + step, sright, step):
            sampling.append(self.sub_interval(left, sright))

        return sampling