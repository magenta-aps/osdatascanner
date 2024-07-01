from os.path import join as joinpath
from time import sleep
import pytest
from tempfile import TemporaryDirectory

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model import file
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.rules import logical
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.utilities.analysis import compute_mss
from os2datascanner.engine2.pipeline import explorer, messages


class TestPreExec:
    @staticmethod
    def make_message_base(td):
        return messages.ScanSpecMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=file.FilesystemSource(td),
                rule=None,
                configuration={},
                progress=None,
                filter_rule=None)

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

    def test_explorer_rule(self):
        """The pipeline's explorer stage correctly propagates rules to Sources
        for pre-execution."""
        with SourceManager() as sm, TemporaryDirectory() as td:
            # Arrange
            with open(joinpath(td, "test_one.txt"), "wt") as fp:
                fp.write("This is the first test file...")
            with open(joinpath(td, "test_two.txt"), "wt") as fp:
                fp.write("... this is the second test file...")

            # Sleep for a second to make sure that the first two files and
            # the last one have differentiable timestamps
            sleep(1)

            after_first_two = time_now()

            with open(joinpath(td, "test_three.txt"), "wt") as fp:
                fp.write("... and this is the FINAL TEST FILE.")

            message = self.make_message_base(td)._replace(
                    rule=LastModifiedRule(after=after_first_two))

            # Act
            message_objects = [
                    messages.ConversionMessage.from_json_object(j)
                    for channel, j in explorer.message_received_raw(
                            message.to_json_object(),
                            "os2ds_scan_specs", sm)
                    if channel == "os2ds_conversions"]
            handle_names = set(msg.handle.name for msg in message_objects)

            # Assert
            assert handle_names == {"test_three.txt"}
