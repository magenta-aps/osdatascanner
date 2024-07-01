import pytest

from os2datascanner.engine2.rules import logical
from os2datascanner.engine2.rules.utilities.analysis import compute_mss


class TestPreExec:
    @pytest.mark.parametrize(
            "rule,mss",
            [
                (None, set()),

                # No way round atoms
                ("A", {"A"}),

                # Every atom named in an AndRule is required
                (logical.AndRule.make("A", "B", "C"), {"A", "B", "C"}),
                # ... no matter how much you try to hide it
                (logical.AndRule.make(
                        "A",
                        needs_bc := logical.AndRule.make("B", "C")),
                 {"A", "B", "C"}),

                # None of the individual atoms named in an OrRule is required
                (logical.OrRule.make("A", "B", "C"), set()),
                # (although it's possible that there may be some atoms required
                # by every branch of the OrRule)
                (needs_b := logical.OrRule.make(
                        logical.AndRule.make("A", "B"), needs_bc),
                 {"B"}),

                # Combinations of AndRule and OrRule work fine too
                (logical.AndRule.make(needs_b, "D"), {"B", "D"}),

                # (NotRules are ignored for now)
                (logical.NotRule.make("A"), set()),
            ])
    def test_mss_computation(self, rule, mss):
        """The minimal set of SimpleRules is calculated correctly."""
        assert compute_mss(rule) == mss
