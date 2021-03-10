import math
from fractions import Fraction
from operator import gt, lt
from typing import Union, Iterator

Bound = Union[int, Fraction]


def step_range(start: Bound, end: Bound, step: Bound) -> Iterator[Bound]:
    if math.isinf(start) or math.isinf(end) or math.isinf(step):
        raise ValueError("An argument is infinite")

    current = start
    op = lt if step > 0 else gt

    while op(current, end):
        yield current
        current += step
