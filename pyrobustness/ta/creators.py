# coding=utf-8
import pyrobustness.ta.timedauto as timed_auto
import pyrobustness.ta.guards as guards
import pyrobustness.ta.exceptions as exceptions

"""
Module to generate from JSON-like the objects of the ta library 
(linearConstraint, LinearGuard,Label, Edge, and TimedAutomaton)
"""


def linear_constraint_creator(lower_bound, upper_bound, clock_index):
    """
    Generate from a JSON-like syntax a linearConstraint
    :param lower_bound: integer, Fraction or math.inf
    :param upper_bound: integer, Fraction or math.inf
    :param clock_index: integer
    :return: a linear_constraint
    -----
    Example:
    {
    'clock_index': 0,
    'lower_bound': 0,
    'upper_bound': 1,
    }
    """
    return guards.LinearConstraint(
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        clock_index=clock_index
    )


def linear_guard_creator(serialized):
    """
    Generate from a JSON-like syntax a linearGuard.
    :param serialized: a list of dict (see example to have the syntax)
    :return: a LinearGuard
    :type: "type" should contains a str, "data" should contain a dictionary of integers
            (or Fraction or math.inf for lower_bound and upper_bound)
    -----
    Example:
    guard_creator([
                {
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": 3,
                        "clock_index": 1
                    }
                },

                {
                    "type": "linear",
                    "data": {
                        "lower_bound": 0,
                        "upper_bound": Fraction(4,10),
                        "clock_index": 0
                    }
                }
         ])
    """
    constraints = []

    for c in serialized:
        if c["type"] != "linear":
            raise exceptions.ConstraintTypeFail(("linear", c["type"]))
        constraints.append(linear_constraint_creator(**c["data"]))

    return guards.LinearGuard(constraints=constraints)


def label_creator(guard_data, resets):
    """
    Generate from a JSON-like syntax a Label.
    :param: guard_data: a list of dict (see linear_guard_creator for the syntax)
    :param: resets: a list of integers
    :return: a Label
    :type: "guard_data" should be a guard crestor type, and resets should be a list of integer.
    ------
    Example:
        label_creator(
                        guard_data={
                            "type": "linear",
                            "constraints": [{
                                "type": "linear",
                                "data": {
                                    'clock_index': 0,
                                    'lower_bound': 0,
                                    'upper_bound': 1,
                                }
                            }]
                        },
                        resets=[]
                    )
    """
    guard = linear_guard_creator(guard_data["constraints"]) if guard_data["type"] == "linear" else None

    if guard is None:
        raise exceptions.UnknownGuardType(guard_data["type"])

    return guards.Label(
        guard=guard,
        resets=resets
    )


def edge_creator(serialized):
    """
    Generate from a JSON-like syntax a linearGuard.
    :param: serialized: a dict
    :return: an edge
    :type: "start_location" and "end_location" should be integers or str,
            "data" should be a label creator type
            and resets should be a list of integer.
    ------
    Example:
        edge_creator(
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 1,
                                    "upper_bound": 2,
                                    "clock_index": 0,
                                },
                            },
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 0,
                                    "upper_bound": 1,
                                    "clock_index": 1,
                                },
                            }
                        ]
                    },
                    "resets": [1],
                }]
            }
                    )
    """
    return timed_auto.Edge(
        start_location=serialized["start_location"],
        end_location=serialized["end_location"],
        data={
            data["action"]: label_creator(
                guard_data=data["guard"],
                resets=data["resets"]) for data in serialized["data"]
        },
    )


def timed_automaton_creator(serialized):
    """
    Generate from a JSON-like syntax a linearGuard.
    :param serialized: a dict
    :return: a TimedAutomaton
    :type: : "Transitions" should contain edge_creator input type
            "init_location" and "goal_location" should contain integer or str
            and "number_clocks" should contains integer.
    -----
    Example:

    timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 1,
                                    "upper_bound": 2,
                                    "clock_index": 0,
                                },
                            },
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 0,
                                    "upper_bound": 1,
                                    "clock_index": 1,
                                },
                            }
                        ]
                    },
                    "resets": [1],
                }]
            },
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 2,
    })

    """
    overwrite = serialized.get("overwrite", None)

    return timed_auto.TimedAutomaton(
        transitions=[edge_creator(t) for t in serialized["transitions"]],
        init_location=serialized["init_location"],
        goal_location=serialized["goal_location"],
        number_clocks=serialized["number_clocks"],
        overwrite=overwrite)
