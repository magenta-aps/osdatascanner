from types import SimpleNamespace
import pytest
import shutil
from pathlib import Path
from datetime import timedelta

from os2datascanner.utils.system_utilities import time_now

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import (
        FilesystemSource, FilesystemHandle)
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
import os2datascanner.engine2.rules.logical_operators  # noqa

from os2datascanner.engine2.pipeline import (
        messages, explorer, worker)
from os2datascanner.engine2.utilities.datetime import NOT_SCANNED_DT


here = Path(__file__)
test_data = here.parent / "data"


@pytest.fixture
def writeable_source():
    with FilesystemSource.make_tmp_folder() as (src, path):
        print(src, path)
        yield SimpleNamespace(source=src, path=path)


def execute_pipeline(message: messages.ScanSpecMessage):
    sm = SourceManager()

    for c1, m1 in explorer.message_received_raw(
            message.to_json_object(), "os2ds_scan_specs", sm):
        match c1:
            case "os2ds_problems":
                yield messages.ProblemMessage.from_json_object(m1)
            case "os2ds_conversions":
                for c2, m2 in worker.message_received_raw(
                        m1, "os2ds_conversions", sm):
                    print("worker sez", c2, m2)
                    match c2:
                        case "os2ds_matches":
                            yield messages.MatchesMessage.from_json_object(m2)
                        case "os2ds_checkups":
                            if messages.ContentSkippedMessage.test(m2):
                                yield messages.ContentSkippedMessage.from_json_object(m2)
                            elif messages.MatchesMessage.test(m2):
                                # These messages have also emitted on the
                                # os2ds_matches queue, so we can drop them here
                                pass
                            else:
                                raise ValueError(":(", c2)
                        case "os2ds_problems":
                            yield messages.ProblemMessage.from_json_object(m2)
                        case "os2ds_metadata":
                            yield messages.MetadataMessage.from_json_object(m2)
                        case "os2ds_status":
                            yield messages.StatusMessage.from_json_object(m2)
                        case _:
                            raise ValueError(":/", c2)
            case "os2ds_status":
                yield messages.StatusMessage.from_json_object(m1)
            case _:
                raise ValueError(";(", c1)


class TestSkip:
    def test_skip(self, *, writeable_source):
        """Image references are emitted when OCR scan is disabled, but their
        content is not scanned."""
        # Arrange
        now = time_now() - timedelta(seconds=5)

        shutil.copy(
                test_data / "ocr" / "good" / "cpr.png",
                writeable_source.path / "cpr.png")

        # Act
        ssm = messages.ScanSpecMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=writeable_source.source,
                rule=LastModifiedRule(after=now) & CPRRule(modulus_11=False),
                configuration={"skip_mime_types": ["image/*"]},
                filter_rule=None,
                progress=None)
        results = [
                om for om in execute_pipeline(ssm)
                if isinstance(om, (messages.MatchesMessage,
                                   messages.ContentSkippedMessage))]

        # Assert
        match results:
            case [
                    messages.ContentSkippedMessage(
                            handle=FilesystemHandle(
                                    relative_path="cpr.png"),
                    ),
            ]:
                pass
            case _:
                raise AssertionError

    def test_revisit_no_change(self, *, writeable_source):
        """Revisiting a skipped image with no change in the OCR setting does
        not cause the content to be scanned."""
        # Arrange
        shutil.copy(
                test_data / "ocr" / "good" / "cpr.png",
                writeable_source.path / "cpr.png")

        # Act
        ssm = messages.ScanSpecMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=writeable_source.source,
                rule=(LastModifiedRule(after=NOT_SCANNED_DT)
                      & CPRRule(modulus_11=False)),
                configuration={"skip_mime_types": ["image/*"]},
                filter_rule=None,
                progress=None)
        results = [
                om for om in execute_pipeline(ssm)
                if isinstance(om, (messages.MatchesMessage,
                                   messages.ContentSkippedMessage))]

        # Assert
        match results:
            case [
                    messages.ContentSkippedMessage(
                            handle=FilesystemHandle(
                                    relative_path="cpr.png"),
                    ),
            ]:
                pass
            case _:
                raise AssertionError

    def test_revisit_after_change(self, *, writeable_source):
        """Revisiting a skipped image after changing the OCR setting causes
        image content to be scanned in the usual manner."""
        # Arrange
        shutil.copy(
                test_data / "ocr" / "good" / "cpr.png",
                writeable_source.path / "cpr.png")

        # Act
        ssm = messages.ScanSpecMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=writeable_source.source,
                rule=(LastModifiedRule(after=NOT_SCANNED_DT)
                      & CPRRule(modulus_11=False)),
                configuration={},
                filter_rule=None,
                progress=None)
        results = [
                om for om in execute_pipeline(ssm)
                if isinstance(om, (messages.MatchesMessage,
                                   messages.ContentSkippedMessage))]

        # Assert
        match results:
            case [
                    messages.MatchesMessage(
                            handle=FilesystemHandle(
                                    relative_path="cpr.png"),
                            matched=True,
                    ),
            ]:
                pass
            case _:
                raise AssertionError
