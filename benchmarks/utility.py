"""
Contains utility functions to help create new benchmarks
"""
from typing import List, Dict, Tuple, Any, Union

Clock = int
BoundTy = Union[float, int]
Bounds = Tuple[BoundTy, BoundTy]
Guards = Dict[Clock, Bounds]
Resets = List[Clock]
TransitionParam = Tuple[Guards, Resets]


def linear_guard_constructor(transition_index: int, param: Guards, resets: Resets) -> Any:
    return {
        "start_location": transition_index,
        "end_location": transition_index + 1,
        "data": [{
            "action": "a_" + str(transition_index + 1),
            "guard": {
                "type": "linear",
                "constraints": [
                    {
                        "type": "linear",
                        "data": {
                            "lower_bound": bounds[0],
                            "upper_bound": bounds[1],
                            "clock_index": clock
                        }
                    } for clock, bounds in param.items()
                ],
            },
            "resets": [x for x in resets],
        }],
    }


def linear_transition_constructor(param: List[TransitionParam]) -> Any:
    return [
        linear_guard_constructor(index, param, resets) for index, (param, resets) in enumerate(param)
    ]


def linear_constructor(param: List[TransitionParam]) -> Any:
    nb_clock = len({c for t in param for c in t[0]})
    return {
        "transitions": [
            transition for transition in linear_transition_constructor(param)
        ],
        "init_location": 0,
        "goal_location": len(param),
        "number_clocks": nb_clock
    }


def same_guard(transition_index: int):
    """
    Generate a linear guard for a given transition with the guard
    0 <= x,y <= 1
    """
    return linear_guard_constructor(transition_index - 1, param={0: (0, 1), 1: (0, 1)}, resets=[])
