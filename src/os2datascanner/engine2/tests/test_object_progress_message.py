# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import uuid

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.messages import (
    ScanTagFragment, ScannerFragment, OrganisationFragment)


def _scan_tag():
    return ScanTagFragment(
            time=messages.parse_datetime("2026-06-22T10:00:00+02:00"),
            scanner=ScannerFragment(pk=1, name="test"),
            user=None,
            organisation=OrganisationFragment(
                    name="Test Org", uuid=uuid.UUID("12345678-1234-5678-1234-567812345678")))


def test_object_progress_roundtrip():
    msg = messages.ObjectProgressMessage(
            scan_tag=_scan_tag(),
            object_key="abc123",
            object_path="huge-bundle.zip (in /share)",
            current_path="report.pdf (in huge-bundle.zip (in /share))",
            items_processed=3412,
            elapsed_seconds=840,
            final=False)

    obj = msg.to_json_object()
    assert obj["type"] == "object_progress"
    assert obj["current_path"] == "report.pdf (in huge-bundle.zip (in /share))"

    restored = messages.ObjectProgressMessage.from_json_object(obj)
    assert restored == msg


def test_object_progress_final_flag_defaults_false():
    msg = messages.ObjectProgressMessage(
            scan_tag=_scan_tag(), object_key="k")
    assert msg.final is False
    assert messages.ObjectProgressMessage.from_json_object(
            msg.to_json_object()).final is False
