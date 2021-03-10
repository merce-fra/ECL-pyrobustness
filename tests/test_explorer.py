# coding=utf-8

from tests.test_explorer_examples import *
import pyrobustness.runs.explorer as explorer
import pyrobustness.ta.timedauto as timed_auto



class TestComputeTracePermissiveness:
    def test(self, trace_0, trace_1, trace_2):
        assert trace_0.compute_trace_permissiveness() == 1
        assert trace_1.compute_trace_permissiveness() == 1
        assert trace_2.compute_trace_permissiveness() == 5


class CompareBestTrace:
    def test(self, trace_1, trace_2, trace_0):  # Verify signs
        assert trace_1.compare_trace(trace_2) > 0
        assert trace_0.compare_trace(trace_2) > 0
        assert trace_0.compare_trace(trace_1) > 0

class TestGoalCond:
    def test(self, formats_exploration_0_0, formats_exploration_1_0,
             formats_exploration_2_0):
        assert formats_exploration_0_0.goal_cond(timed_auto.Configuration(3, [0, 0]))
        assert not formats_exploration_0_0.goal_cond(timed_auto.Configuration(2, [0, 0]))
        assert not formats_exploration_0_0.goal_cond(timed_auto.Configuration(1, [0, 0]))
        assert not formats_exploration_0_0.goal_cond(timed_auto.Configuration(0, [0, 0]))

        assert formats_exploration_1_0.goal_cond(timed_auto.Configuration(2, [0, 0]))
        assert not formats_exploration_1_0.goal_cond(timed_auto.Configuration(1, [0, 0]))
        assert not formats_exploration_1_0.goal_cond(timed_auto.Configuration(0, [0, 0]))

        assert formats_exploration_2_0.goal_cond(timed_auto.Configuration(2, [0, 0]))
        assert not formats_exploration_2_0.goal_cond(timed_auto.Configuration(1, [0, 0]))
        assert not formats_exploration_2_0.goal_cond(timed_auto.Configuration(0, [0, 0]))





# class TestFailCond:
#     def test(self, trace_199_long, trace_200_long, trace_201_long, trace_300_long, trace_0, trace_1):
#         # TODO: Requires to create a new explorer with the right bounds
#         # TODO: Also test cycle bound
#         assert not explorer.Backtracking.fail_cond(trace_0)
#         assert not explorer.Backtracking.fail_cond(trace_1)
#         assert not explorer.Backtracking.fail_cond(trace_199_long)
#         assert explorer.Backtracking.fail_cond(trace_200_long)
#         assert explorer.Backtracking.fail_cond(trace_201_long)
#         assert explorer.Backtracking.fail_cond(trace_300_long)


#
#
# class TestApplyFail:
#     def test(self):
#         pass


class TestFilterPoss:
    def test(self):
        # Trace_0 and trace_1 has permissiveness 1, trace_2 has permissiveness 5
        pass


class TestExtractMaxInterval:
    def test(self):
        pass


class TestGenNextPoss:
    def test(self):
        pass


class TestSamplingOpponent:
    def test(self):
        pass


class TestBacktrackDelay:
    def test(self):
        pass


class TestBacktrack:
    def test(self, formats_exploration_0_precise):
        assert formats_exploration_0_precise.backtracking().compute_trace_permissiveness(
            ) == 1

        # explo = formats_exploration_2_precise([0.5, 0.3], 0.5)
        # assert explo.compute_trace_permissiveness(explo.backtracking()) == 2
