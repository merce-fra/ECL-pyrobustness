# coding=utf-8

class OpenInterval(Exception):
    """
    Raised when an interval is open at left or right side, and when a
    function ask for the exact bound of the interval.
    """

    def __init__(self, used_fct, interval, right_function):
        super().__init__(used_fct + " use only closed interval, interval " + interval +
                         " is open. Please use the function " + right_function + " instead")


class StepOutOfBound(Exception):
    """
    Raised when an interval is open at left or right side, and when a
    function ask for the exact bound of the interval.
    """

    def __init__(self):
        super().__init__("The approximation step is too great")


class CycleException(Exception):
    pass


# class TimedAutomatonNonSingleAction(Exception):
#     """
#     TODO
#     """
#
#     def __init__(self):
#         super().__init__("This function is not implemented for "
#                          "non-single-action timed automaton")


class WrongTimedAutomatonClass(Exception):

    def __init__(self, fct, ta_class):
        super().__init__(fct + " not implemented for " + ta_class + "timed automaton")


# class NonDeterministicTimedAutomaton(Exception):
#     """
#     TODO
#     """
#
#     def __init__(self):
#         super().__init__()


class StepNotFound(Exception):
    def __init__(self, m):
        super().__init__(m)


class DelayNotFound(Exception):
    def __init__(self, place, delay=""):
        super().__init__("Unable to find delay " + delay + " in " + place)


class IntervalNotFound(Exception):
    def __init__(self, interval):
        super().__init__("Interval " + interval + "not found")


class WrongType(Exception):
    def __init__(self, right_type, element):
        super().__init__(element + " should be " + right_type)


class InfinitePathFound(Exception):
    def __init__(self):
        super().__init__("Backtracking is useless because there exists a path such "
                       "that all upper bounds are inifnite. Permissiveness is infinite.")


class BoundException(Exception):
    pass
