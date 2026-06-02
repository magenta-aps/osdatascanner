# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os.path
from datetime import datetime
from uuid import UUID

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.core.handle import Handle
from os2datascanner.engine2.model.derived.mail import MailPartHandle, MailSource
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.utilities.backoff import TimeoutRetrier

from os2datascanner.engine2.pipeline.messages import (
    ConversionMessage,
    ScanSpecMessage,
    ScanTagFragment,
    ScannerFragment,
    OrganisationFragment,
    ProgressFragment,
    RepresentationMessage,
)

from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.dict_lookup import EmailHeaderRule

from os2datascanner.engine2.pipeline.processor import (
    message_received, message_received_raw, do_conversion)


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "mail")
test_file_path = os.path.join(test_data_path, "subject_and_image.eml")


def _scan_spec(rule, progress, *, configuration=None):
    return ScanSpecMessage(
        scan_tag=ScanTagFragment(
            time=datetime.fromisoformat("2091-10-29T13:46:51+01:00"),
            user="vejstrand@placeholder.invalid",
            scanner=ScannerFragment(pk=1, name="Vejstrand Test suite"),
            organisation=OrganisationFragment(
                name="Vejstrand",
                uuid=UUID("ddaf961b-da39-4b03-a45f-350896b2781b"),
            ),
        ),
        source=FilesystemSource(path=test_data_path),
        rule=rule,
        configuration=configuration or {},
        filter_rule=None,
        progress=progress,
    )


def test_processor_on_email_image_can_find_email_header():
    """ A processor has unpacked an email and traversed (converted) down
    to an image in it, to then be asked to acquire email header data."""

    # Arrange

    # An unpacked email - an image in it.
    handle = MailPartHandle(
        MailSource(
            FilesystemHandle.make_handle(test_file_path),
        ),
        path="1/img_001.png",
        mime="image/png"
    )

    # Next rule we are to evaluate: EmailHeaderRule
    rule = EmailHeaderRule(prop="subject", rule=CPRRule())
    progress_fragment = ProgressFragment(rule=rule, matches=[])

    conversion_message = ConversionMessage(
        scan_spec=_scan_spec(rule, progress_fragment),
        handle=handle,
        progress=progress_fragment,
    )

    # Act
    for channel, message in message_received_raw(
            conversion_message.to_json_object(), "os2ds_conversions", SourceManager()):

        # Assert
        # Should ultimately lead to a representation message, now containing email-headers.
        repr_msg = RepresentationMessage.from_json_object(message)
        assert channel == "os2ds_representations"
        assert repr_msg.representations["email-headers"]


def test_processor_aborts_before_conversion():
    """message_received() with should_abort=lambda: True must yield nothing,
    even when the underlying handle points at a real file."""
    handle = MailPartHandle(
        MailSource(FilesystemHandle.make_handle(test_file_path)),
        path="1/img_001.png",
        mime="image/png",
    )
    progress = ProgressFragment(rule=CPRRule(), matches=[])
    msg = ConversionMessage(
            scan_spec=_scan_spec(CPRRule(), progress), handle=handle, progress=progress)

    results = list(message_received(
            msg, SourceManager(), _check=False, should_abort=lambda: True))
    assert results == []


def test_email_headers_served_from_ancestor_hint():
    """When the mail handle has a populated 'email-headers' hint, deriving
    EmailHeaders for a child object is served from that hint instead of
    re-converting the mail."""

    sm = SourceManager()
    # If we really parsed the .eml file on test_file_path, we'd get a different subject.
    # So, intentionally fiddling with it to showcase that we're reading it from the hint.
    HINT = {"subject": "HINT SUBJECT"}
    mail = FilesystemHandle.make_handle(
            test_file_path, hints={"email-headers": HINT})
    child = next(iter(MailSource(mail).handles(sm)))
    rule = EmailHeaderRule(prop="subject", rule=CPRRule())
    progress = ProgressFragment(rule=rule, matches=[])
    conv = ConversionMessage(
            scan_spec=_scan_spec(rule, progress), handle=child, progress=progress)

    headers = do_conversion(
            child.follow(sm), conv, TimeoutRetrier(seconds=60, max_tries=1), sm)

    assert headers == HINT
    assert headers.parent is None


def test_mail_handle_hint_survives_serialisation():
    sm = SourceManager()
    mail_handle = FilesystemHandle.make_handle(
            test_file_path, hints={"email-headers": {"subject": "HINT SUBJECT"}})
    child = next(iter(MailSource(mail_handle).handles(sm)))

    restored = Handle.from_json_object(child.to_json_object())

    found = [h.hint("email-headers")
             for h in restored.walk_up() if h.hint("email-headers")]
    assert found == [{"subject": "HINT SUBJECT"}]
