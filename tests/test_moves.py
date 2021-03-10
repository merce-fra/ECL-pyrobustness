# coding=utf-8
import pyrobustness.runs.moves as moves
import pyrobustness.ta.interval
from pyrobustness.ta.timedauto import Configuration
import pyrobustness.ta.guards as guards
import pyrobustness.runs.opponentstrategy as opponent_strategy
from tests.test_moves_examples import *
from tests.test_timedauto_examples import *


class TestMethods:

    def test_valuation_after_passing_guard(self):
        # label = Label(
        #     guard=guard,
        #     resets=[]
        # )
        pass

    def test_valuation_after_passing_guard_permissive(self):
        pass

    def test_moves(self):
        pass

    def test_next_step(self):
        pass

    def test_next_step_permissive(self, timed_automaton_0):
        config = Configuration(location=0,
                               valuation=[0])

        move = {
            "action": 'a',
            "step": [
                moves.Step(interval=pyrobustness.ta.interval.Interval(0, 1), target_location=1)
            ]
        }
        strategy = opponent_strategy.worst_case_branch_free_opponent_strategy()

        final_configs = moves.next_step_permissive(timed_automaton=timed_automaton_0,
                                                   configuration=config,
                                                   move=move,
                                                   strategy=strategy)

        assert Configuration(location=1, valuation=[0]) in final_configs
        assert Configuration(location=1, valuation=[1]) in final_configs


class TestComputeIntervalLength:

    def test(self, standard_move, two_step_move):
        assert moves.compute_interval_length(standard_move) == 1
        assert moves.compute_interval_length(two_step_move) == 5


class TestMoveSampling:
    def test(self, empty_move, standard_move, standard_move_expected_sampling_0_5,
             two_step_move, two_step_move_expected_sampling_1):
        with pytest.raises(Exception):
            moves.move_sampling(empty_move, Fraction(3, 5))
        assert moves.move_sampling(standard_move, Fraction(1, 2)) == \
               standard_move_expected_sampling_0_5

        assert moves.move_sampling(two_step_move, 1) == \
               two_step_move_expected_sampling_1
