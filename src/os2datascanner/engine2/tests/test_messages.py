# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from dataclasses import dataclass

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.rules.dummy import AlwaysMatchesRule


@dataclass(frozen=True, slots=True, kw_only=True)
class SampleTuple:
    field1: str
    field2: int
    field3: bool | str | None
    field4: object = None


class TestMessage:
    def test_deep_replacement(self):
        a = SampleTuple(
                field1="Hello",
                field2=12345,
                field3=True,
                field4=SampleTuple(
                        field1="Goodbye",
                        field2=67890,
                        field3=False,
                        field4=SampleTuple(
                                field1="",
                                field2=0,
                                field3=None)))

        # Test simple replacement
        assert messages.deep_replace(a, field1="Hi").field1 == "Hi"
        # Test 1-level deep replacement
        assert messages.deep_replace(a, field4__field1="Bye").field4.field1 == "Bye"
        # Test deeper replacement
        assert messages.deep_replace(
            a, field4__field4__field3="FileNotFound").field4.field4.field3 == "FileNotFound"
        # Test multiple replacements at different levels
        b = messages.deep_replace(a,
                                  field1="Goddag",
                                  field2=7-9-13,
                                  field3="Sandt",
                                  field4__field1="Farvel",
                                  field4__field2=117,
                                  field4__field3="Falsk",
                                  field4__field4=None)
        assert b == SampleTuple(
                        field1="Goddag",
                        field2=-15,
                        field3="Sandt",
                        field4=SampleTuple(
                                field1="Farvel",
                                field2=117,
                                field3="Falsk"))

    def test_old_scan_tag_parsing(self):
        """scan tag from versions 3.0.0-3.3.2"""
        stf = messages.ScanTagFragment.from_json_object(
                "2019-12-20T09:00:00+01:00")
        assert stf.time == datetime.datetime(
                                2019, 12, 20,
                                9, 0, 0,
                                tzinfo=datetime.timezone(
                                        datetime.timedelta(seconds=3600)))

    def test_old_scan_tag_parsing2(self):
        """scan tag from versions 3.3.3-3.6.0"""
        stf = messages.ScanTagFragment.from_json_object({
            "time": "2020-06-24T09:00:00+01:00",
            "user": "jens",
            "scanner": {
                "pk": 10,
                "name": "Test scanner",
                "test": False,
            },
            "organisation": "Vejstrand Kommune"
        })
        assert stf.organisation == messages.OrganisationFragment(
            name="Vejstrand Kommune", uuid=None)

    def test_problem_missing_compat(self):
        """Old-fashioned ContentMissingMessages (based on ProblemMessage) can
        be parsed."""
        # Arrange
        jf = {
            "scan_tag": messages.ScanTagFragment.make_dummy().to_json_object(),
            "handle": {
                "type": "file",
                "source": {
                    "type": "file",
                    "path": "/home/af",
                },
                "path": "path/to/document.txt",
            },
            "missing": True,
            "message": "It's gone, boss"
        }
        # Act
        mo = messages.ProblemMessage.from_json_object(jf)
        # Assert
        assert isinstance(mo, messages.ContentMissingMessage)
        assert mo.handle.relative_path == "path/to/document.txt"

    def test_problem_irrelevant_compat(self):
        """Old-fashioned ContentIrrelevantMessages (based on ProblemMessage)
        can be parsed."""
        # Arrange
        jf = {
            "scan_tag": messages.ScanTagFragment.make_dummy().to_json_object(),
            "handle": {
                "type": "file",
                "source": {
                    "type": "file",
                    "path": "/home/af",
                },
                "path": "path/to/second-document.txt",
            },
            "irrelevant": True,
            "message": "Not part of the scan no more"
        }
        # Act
        mo = messages.ProblemMessage.from_json_object(jf)
        # Assert
        assert isinstance(mo, messages.ContentIrrelevantMessage)
        assert mo.handle.relative_path == "path/to/second-document.txt"

    def test_problem_message_account_uuid_roundtrip(self):
        problem = messages.ProblemMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=None, handle=None, message="boom",
                account_uuid="11111111-1111-1111-1111-111111111111")
        rehydrated = messages.ProblemMessage.from_json_object(problem.to_json_object())
        assert rehydrated.account_uuid == "11111111-1111-1111-1111-111111111111"

    def test_problem_message_account_uuid_defaults_to_none(self):
        problem = messages.ProblemMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=None, handle=None, message="boom")
        obj = problem.to_json_object()
        assert obj["account_uuid"] is None
        rehydrated = messages.ProblemMessage.from_json_object(obj)
        assert rehydrated.account_uuid is None

    def test_problem_message_account_uuid_absent_field_defaults_to_none(self):
        """A ProblemMessage serialized before this field existed (no
        "account_uuid" key at all) must still deserialize cleanly."""
        problem = messages.ProblemMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=None, handle=None, message="boom")
        obj = problem.to_json_object()
        del obj["account_uuid"]
        rehydrated = messages.ProblemMessage.from_json_object(obj)
        assert rehydrated.account_uuid is None


class TestCommandMessage:
    def test_new_queue_roundtrip(self):
        msg = messages.CommandMessage(
                new_queue="osds_conversions.42_20240101T120000",
                new_queue_priority="delta")
        restored = messages.CommandMessage.from_json_object(msg.to_json_object())
        assert restored.new_queue == "osds_conversions.42_20240101T120000"
        assert restored.new_queue_priority == "delta"
        assert restored.delete_queue is None
        assert restored.worker_hello is None

    def test_delete_queue_roundtrip(self):
        msg = messages.CommandMessage(
                delete_queue="osds_conversions.42_20240101T120000")
        restored = messages.CommandMessage.from_json_object(msg.to_json_object())
        assert restored.delete_queue == "osds_conversions.42_20240101T120000"
        assert restored.new_queue is None

    def test_worker_hello_roundtrip(self):
        msg = messages.CommandMessage(worker_hello="amq.gen-abc123")
        restored = messages.CommandMessage.from_json_object(msg.to_json_object())
        assert restored.worker_hello == "amq.gen-abc123"
        assert restored.abort is None

    def test_default_fields_are_none(self):
        msg = messages.CommandMessage()
        obj = msg.to_json_object()
        assert obj["new_queue"] is None
        assert obj["new_queue_priority"] is None
        assert obj["delete_queue"] is None
        assert obj["worker_hello"] is None


class TestScanSpecMessageAccountUuid:
    def _make_spec(self, **kwargs):
        return messages.ScanSpecMessage(
                scan_tag=messages.ScanTagFragment.make_dummy(),
                source=FilesystemSource("/usr/share/common-licenses"),
                rule=AlwaysMatchesRule(),
                configuration={},
                progress=None,
                filter_rule=None,
                **kwargs)

    def test_roundtrip(self):
        spec = self._make_spec(account_uuid="11111111-1111-1111-1111-111111111111")
        rehydrated = messages.ScanSpecMessage.from_json_object(spec.to_json_object())
        assert rehydrated.account_uuid == "11111111-1111-1111-1111-111111111111"

    def test_defaults_to_none(self):
        spec = self._make_spec()
        obj = spec.to_json_object()
        assert obj["account_uuid"] is None
        rehydrated = messages.ScanSpecMessage.from_json_object(obj)
        assert rehydrated.account_uuid is None

    def test_absent_field_defaults_to_none(self):
        """A ScanSpecMessage serialized before this field existed (no
        "account_uuid" key at all) must still deserialize cleanly."""
        obj = self._make_spec().to_json_object()
        del obj["account_uuid"]
        rehydrated = messages.ScanSpecMessage.from_json_object(obj)
        assert rehydrated.account_uuid is None
