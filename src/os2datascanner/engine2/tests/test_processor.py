import os.path
from datetime import datetime
from uuid import UUID

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.derived.mail import MailPartHandle, MailSource
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource

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

from os2datascanner.engine2.pipeline.processor import message_received_raw


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "mail")
test_file_path = os.path.join(test_data_path, "subject_and_image.eml")


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
    progress_fragment = ProgressFragment(
            rule=EmailHeaderRule(
                prop="subject", rule=CPRRule(),
            ),
            matches=[]
        )

    scan_spec_msg = ScanSpecMessage(
        scan_tag=ScanTagFragment(
            time=datetime.fromisoformat("2091-10-29T13:46:51+01:00"),
            user="vejstrand@placeholder.invalid",
            scanner=ScannerFragment(
                pk=247857987,
                name="Vejstrand Test suite",
            ),
            organisation=OrganisationFragment(
                name="Vejstrand",
                uuid=UUID("ddaf961b-da39-4b03-a45f-350896b2781b"),
            ),
        ),
        source=FilesystemSource(path=test_data_path),
        rule=EmailHeaderRule(prop="subject", rule=CPRRule()),
        configuration={},
        filter_rule=None,
        progress=progress_fragment
    )

    conversion_message = ConversionMessage(
        scan_spec=scan_spec_msg,
        handle=handle,
        progress=progress_fragment
    )

    # Act
    for channel, message in message_received_raw(
            conversion_message.to_json_object(), "os2ds_conversions", SourceManager()):

        # Assert
        # Should ultimately lead to a representation message, now containing email-headers.
        repr_msg = RepresentationMessage.from_json_object(message)
        assert channel == "os2ds_representations"
        assert repr_msg.representations["email-headers"]
