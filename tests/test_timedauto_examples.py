# coding=utf-8
import math

from pyrobustness.ta.creators import *
from tests.test_guards_examples import *


# Example of ta

@pytest.fixture(autouse=True)
def timed_automaton_infinite():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0
                            }
                        }],
                    },
                    "resets": [],
                }],
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "c",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0
                            }
                        }]
                    },
                    "resets": [],
                }],
            }
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 1
    })


# Timed automaton with transition_0 and transition_2
# Goal: tests 1) init 2) well-formed 3) equality with multiple transitions
# and one-clock
@pytest.fixture(autouse=True)
def timed_automaton_0():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 0
                            }
                        }],
                    },
                    "resets": [],
                }],
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "c",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0
                            }
                        }]
                    },
                    "resets": [],
                }],
            }
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 1
    })


# A clone of timed_automaton_0 with the set of location inverted. Check if
# indexation matters and if add_transition works (give the same ta)

# TODO: Manipulation of the automaton should be visible in the tests
@pytest.fixture(autouse=True)
def timed_automaton_0_clone(transition_2):
    automata = timed_automaton_creator({
        "transitions": [{
            "start_location": 0,
            "end_location": 1,
            "data": [{
                "guard": {
                    "type": "linear",
                    "constraints": [{
                        "type": "linear",
                        "data": {
                            "lower_bound": 0,
                            "upper_bound": 1,
                            "clock_index": 0
                        }
                    }]
                },
                "resets": [],
                "action": "a",
            }],
        }],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 1
    })
    automata.add_transitions([transition_2])
    automata.is_well_formed()
    return automata


# A false-clone timed_automaton_0: the locations don't have the same name

@pytest.fixture(autouse=True)
def timed_automaton_0_false_clone():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 2,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 0
                            },
                        }],
                    },
                    "resets": [],
                }]
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0
                            },
                        }],
                    },
                    "resets": [],
                }]
            },
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 1
    })


# Same, not the same upper guards: check if it does not work
@pytest.fixture(autouse=True)
def timed_automaton_0_false_guard_1():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 3,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            }
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 1
    })


@pytest.fixture(autouse=True)
def timed_automaton_0_false_guard_2():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 3,
                                "upper_bound": +inf,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            }
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 1,
    })


@pytest.fixture(autouse=True)
def timed_automaton_0_false_guard_3():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 1,
                            },
                        }]
                    },
                    "resets": [],
                }]
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            }
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 2,
    })


# TODO: Check same timed_automaton_0
@pytest.fixture(autouse=True)
def timed_automaton_0_bis():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 1,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            }
        ],
        "init_location": 0,
        "goal_location": 1,
        "number_clocks": 1
    })


# Same, but not the same resets: check if it does not work
@pytest.fixture(autouse=True)
def timed_automaton_0_false_reset():
    return timed_automaton_creator({
        "transitions": [
            {
                "start_location": 0,
                "end_location": 2,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": 1,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [1],
                }]
            },
            {
                "start_location": 0,
                "end_location": 0,
                "data": [{
                    "action": "a",
                    "guard": {
                        "type": "linear",
                        "constraints": [{
                            "type": "linear",
                            "data": {
                                "lower_bound": 0,
                                "upper_bound": +inf,
                                "clock_index": 0,
                            },
                        }]
                    },
                    "resets": [],
                }]
            }
        ],
        "init_location": 0,
        "goal_location": 2,
        "number_clocks": 1,
    })


# Test with a multiple-guard timed_automaton and non empty set of resets
@pytest.fixture(autouse=True)
def timed_automaton_1():
    return timed_automaton_creator({
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
                                    "lower_bound": 0,
                                    "upper_bound": 1,
                                    "clock_index": 0,
                                },
                            },
                            {
                                "type": "linear",
                                "data": {
                                    "lower_bound": 2,
                                    "upper_bound": 3,
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


# Testing well-formed timed-automaton: See in tests file.

# Testing change location
@pytest.fixture(autouse=True)
def timed_automaton_loc_0():
    automata = timed_automaton_creator({
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

    automata.change_start_location(1)
    return automata


@pytest.fixture(autouse=True)
def timed_automaton_loc_1():
    return timed_automaton_creator({
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
        "init_location": 1,
        "goal_location": 1,
        "number_clocks": 2,
    })


@pytest.fixture(autouse=True)
def timed_automaton_loc_2():
    automata = timed_automaton_creator({
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
        "init_location": 1,
        "goal_location": 0,
        "number_clocks": 2,
    })

    automata.change_end_location(1)
    return automata


@pytest.fixture(autouse=True)
def timed_automaton_6():
    return timed_automaton_creator({
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
