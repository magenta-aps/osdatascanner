import hashlib
import pytest

from django.test import TestCase
from parameterized import parameterized

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.dimensions import DimensionsRule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.utilities.datetime import parse_datetime
from os2datascanner.engine2.model.smb import SMBSource, SMBHandle

from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.management.commands import result_collector

from .generate_test_data import record_match, record_problem


time0 = "2020-10-28T13:51:49+01:00"
time1 = "2020-10-28T14:21:27+01:00"
time2 = "2020-10-28T14:36:20+01:00"

org_frag = messages.OrganisationFragment(
    name="test_org", uuid="d92ff0c9-f066-40dc-a57e-541721b6c23e")

scan_tag0 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner"),
    time=parse_datetime(time0),
    user=None, organisation=org_frag)
scan_tag1 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner"),
    time=parse_datetime(time1),
    user=None, organisation=org_frag)
scan_tag2 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner"),
    time=parse_datetime(time2), user=None, organisation=org_frag)
scan_tag3 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
        pk=22, name="Dummy test scanner", keep_fp=True),
    time=parse_datetime(time1),
    user=None, organisation=org_frag)
scan_tag4 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
        pk=22, name="Dummy test scanner", keep_fp=False),
    time=parse_datetime(time1),
    user=None, organisation=org_frag)
scan_tag5 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner", test=True),
    time=parse_datetime(time0), user=None, organisation=org_frag)
scan_tag6 = messages.ScanTagFragment(
    scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner", test=True),
    time=parse_datetime(time1), user=None, organisation=org_frag)

common_handle = FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
        "OS2datascanner/Dokumenter/Verdensherredømme - plan.txt")

common_handle_corrupt = FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
        "/logo/Flag/Gr\udce6kenland.jpg")

common_rule = RegexRule("Vores hemmelige adgangskode er",
                        sensitivity=Sensitivity.WARNING)
dimension_rule = DimensionsRule()

common_scan_spec = messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=common_handle.source,
        rule=common_rule,
        configuration={},
        filter_rule=None,
        progress=None)

common_scan_spec_corrupt = messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=common_handle_corrupt.source,
        rule=common_rule,
        configuration={},
        filter_rule=None,
        progress=None)

positive_match = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])

positive_match_keep_fp = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag3),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])

positive_match_dont_keep_fp = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag4),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])

positive_match_corrupt = messages.MatchesMessage(
        scan_spec=common_scan_spec_corrupt._replace(scan_tag=scan_tag0),
        handle=common_handle_corrupt,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])

positive_match_with_dimension_rule_probability_and_sensitivity = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object",
                          "probability": 0.6, "sensitivity": 750},
                         {"dummy1": "match object",
                          "probability": 0.0, "sensitivity": 1000},
                         {"dummy2": "match object",
                          "probability": 1.0, "sensitivity": 500}]),
            messages.MatchFragment(
                rule=dimension_rule,
                matches=[{"match": [2496, 3508]}])
        ])

positive_match_only_notify_superadmin = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag5),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])

positive_match_only_notify_superadmin_later = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag6),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])

negative_match = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(
            scan_tag=scan_tag1),
        handle=common_handle,
        matched=False,
        matches=[messages.MatchFragment(
                rule=common_rule,
                matches=[])
        ])

deletion = messages.ProblemMessage(
        scan_tag=scan_tag1,
        source=None,
        handle=common_handle,
        message="There was a file here. It's gone now.",
        missing=True)

transient_handle_error = messages.ProblemMessage(
        scan_tag=scan_tag1,
        source=None,
        handle=common_handle,
        message="Bad command or file name")

transient_source_error = messages.ProblemMessage(
        scan_tag=scan_tag1,
        source=common_handle.source,
        handle=None,
        message="Not ready reading drive A: [A]bort, [R]etry, [F]ail?")

late_rule = LastModifiedRule(parse_datetime(time2))
late_negative_match = messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(
                scan_tag=scan_tag2,
                rule=AndRule(
                        late_rule,
                        common_rule)),
        handle=common_handle,
        matched=False,
        matches=[messages.MatchFragment(
                rule=late_rule,
                matches=[])])

smb_source_1 = SMBSource('//some/path', user='egon_olsen', driveletter='Q')
smb_source_2 = SMBSource('//some/path', user='dynamit_harry', driveletter='Q')
smb_source_3 = SMBSource('//some/path', user='egon_olsen', driveletter='W')
smb_handle_1 = SMBHandle(smb_source_1, 'filename.file')
smb_handle_2 = SMBHandle(smb_source_2, 'filename.file')
smb_handle_3 = SMBHandle(smb_source_3, 'filename.file')

smb_match_1 = messages.MatchesMessage(
    scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
    handle=smb_handle_1,
    matched=True,
    matches=[
        messages.MatchFragment(
            rule=common_rule,
            matches=[{"dummy": "match object"}])
    ]
)
smb_match_2 = messages.MatchesMessage(
    scan_spec=common_scan_spec._replace(scan_tag=scan_tag1),
    handle=smb_handle_2,
    matched=True,
    matches=[
        messages.MatchFragment(
            rule=common_rule,
            matches=[{"dummy": "match object"}])
    ]
)
smb_match_3 = messages.MatchesMessage(
    scan_spec=common_scan_spec._replace(scan_tag=scan_tag2),
    handle=smb_handle_3,
    matched=True,
    matches=[
        messages.MatchFragment(
            rule=common_rule,
            matches=[{"dummy": "match object"}])
    ]
)


class PipelineCollectorTests(TestCase):
    def test_rejection(self):
        """Failed match messages shouldn't be stored in the database."""
        new = record_match(negative_match)
        self.assertEqual(
                new,
                None,
                "negative match was saved anyway")

    @parameterized.expand([
        ('positive match',
         positive_match,
         [None, None, positive_match.scan_spec.scan_tag.time,
          common_handle.source.type_label]),
        ('positive corrupted match',
         positive_match_corrupt,
         [None, None, positive_match_corrupt.scan_spec.scan_tag.time,
          common_handle_corrupt.source.type_label]),
    ])
    @pytest.mark.filterwarnings("ignore:stripping illegal surrogates for PostgreSQL compatibility")
    # We expect to get a warning because of the corrupted match
    def test_acceptance(self, _, match, expected):
        """Successful match messages should be stored in the database."""
        new = record_match(match)
        self.assertNotEqual(
                new.pk,
                expected[0],
                "positive match was not saved")
        self.assertEqual(
                new.resolution_status,
                expected[1],
                "fresh match was already resolved")
        self.assertEqual(
                new.scan_time,
                expected[2],
                "match time was not taken from scan specification")
        self.assertEqual(
                new.source_type,
                expected[3],
                "type label was not extracted to database")

    def test_edit(self):
        """Removing matches from a file should update the status of the
        previous match message, and should set the resolution time."""
        start = time_now()

        saved_match = record_match(positive_match)
        self.test_rejection()
        saved_match.refresh_from_db()

        self.assertEqual(
                saved_match.resolution_status,
                DocumentReport.ResolutionChoices.EDITED.value,
                "resolution status not correctly updated")
        self.assertGreaterEqual(
                saved_match.resolution_time,
                start,
                "resolution time not correctly updated")

    def test_removal(self):
        """Deleting a file should update the status of the previous match
        message, and should set the resolution time."""
        start = time_now()

        saved_match = record_match(positive_match)
        record_problem(deletion)
        saved_match.refresh_from_db()

        self.assertEqual(
                saved_match.resolution_status,
                DocumentReport.ResolutionChoices.REMOVED.value,
                "resolution status not correctly updated")
        self.assertGreaterEqual(
                saved_match.resolution_time,
                start,
                "resolution time not correctly updated")

    def test_removal_problem(self):
        """Deleting a file, which was previously the source of a problem but
        not a match, should delete the previously created DocumentReport."""
        problem_report = record_problem(transient_handle_error)
        record_problem(deletion)

        self.assertRaises(
                DocumentReport.DoesNotExist,
                problem_report.refresh_from_db)

    def test_transient_handle_errors(self):
        """Source types should be correctly extracted from Handle errors."""
        new = record_problem(transient_handle_error)

        self.assertEqual(
                new.source_type,
                transient_handle_error.handle.source.type_label,
                "type label was not extracted to database")

    def test_transient_source_errors(self):
        """Source types should be correctly extracted from Source errors."""
        new = record_problem(transient_source_error)

        self.assertEqual(
                new.source_type,
                transient_source_error.source.type_label,
                "type label was not extracted to database")

    def test_recycler(self):
        """Receiving a failed match message which failed because of the
        Last-Modified check should update the timestamp of the previous match
        message, but should not create a new database object."""
        saved_match = record_match(positive_match)
        new = record_match(late_negative_match)

        self.assertEqual(
                new,
                None,
                "negative match was saved anyway")
        saved_match.refresh_from_db()
        self.assertEqual(
                saved_match.scan_time,
                parse_datetime(time2),
                "match timestamp not correctly updated")
        self.assertEqual(
                saved_match.resolution_status,
                None,
                "resolution status changed(?!)")

    def test_decycler(self):
        """Receiving a failed match for an object that already had matches
        should blank out those matches, as they are no longer readable."""
        saved_match = record_match(positive_match)
        new = record_problem(transient_handle_error)

        self.assertEqual(
                new,
                saved_match,
                "object with matches not reused for problem")
        self.assertIsNone(
                new.raw_metadata,
                "metadata incorrectly reused for problem")

    def test_filter_internal_rules_matches(self):
        match_to_match = messages.MatchesMessage(
            scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
            handle=common_handle,
            matched=True,
            matches=[
                messages.MatchFragment(
                    rule=common_rule,
                    matches=[{"dummy2": "match object",
                              "probability": 1.0, "sensitivity": 500},
                             {"dummy": "match object",
                              "probability": 0.6, "sensitivity": 750},
                             {"dummy1": "match object",
                              "probability": 0.0, "sensitivity": 1000}]),
                messages.MatchFragment(
                    rule=dimension_rule,
                    matches=[{"match": [2496, 3508]}])
            ])

        self.assertEqual(result_collector.sort_matches_by_probability(
            positive_match_with_dimension_rule_probability_and_sensitivity.to_json_object()  # noqa E501
        )["matches"], match_to_match.to_json_object()["matches"])

    @pytest.mark.filterwarnings("ignore:stripping illegal surrogates for PostgreSQL compatibility")
    # We expect to get a warning because of the corrupted match
    def test_path_format_of_matches(self):
        """Check that recording the matches correctly crunches the handles
        to the `path`-field."""
        pos_match = record_match(positive_match)
        cor_match = record_match(positive_match_corrupt)
        dps_match = record_match(positive_match_with_dimension_rule_probability_and_sensitivity)

        self.assertEqual(
            pos_match.path,
            hashlib.sha512("FilesystemHandle(_source=(FilesystemSource(_path=/mnt/fs01.magenta.dk/brugere/af));_relpath=OS2datascanner/Dokumenter/Verdensherred\xf8mme - plan.txt)".encode("unicode_escape")).hexdigest(),  # noqa E501
            "MatchMessage was not crunched correctly.")
        self.assertEqual(
            cor_match.path,
            hashlib.sha512("FilesystemHandle(_source=(FilesystemSource(_path=/mnt/fs01.magenta.dk/brugere/af));_relpath=/logo/Flag/Gr\udce6kenland.jpg)".encode("unicode_escape")).hexdigest(),  # noqa E501
            "MatchMessage was not crunched correctly.")
        self.assertEqual(
            dps_match.path,
            hashlib.sha512("FilesystemHandle(_source=(FilesystemSource(_path=/mnt/fs01.magenta.dk/brugere/af));_relpath=OS2datascanner/Dokumenter/Verdensherred\xf8mme - plan.txt)".encode("unicode_escape")).hexdigest(),  # noqa E501
            "MatchMessage was not crunched correctly.")

    def test_crunching_handles(self):
        """Check that handles are crunched correctly."""
        smb_crunched_1 = smb_handle_1.crunch(hash=True)
        smb_crunched_2 = smb_handle_2.crunch(hash=True)
        smb_crunched_3 = smb_handle_3.crunch(hash=True)

        self.assertEqual(
            smb_crunched_1,
            hashlib.sha512("SMBHandle(_source=(SMBSource(_unc=//some/path;_user=egon_olsen));_relpath=filename.file)".encode("unicode_escape")).hexdigest(),  # noqa E501
            "SMBHandle was not crunched correctly.")
        self.assertEqual(
            smb_crunched_2,
            hashlib.sha512("SMBHandle(_source=(SMBSource(_unc=//some/path;_user=dynamit_harry));_relpath=filename.file)".encode("unicode_escape")).hexdigest(),  # noqa E501
            "SMBHandle was not crunched correctly.")
        self.assertEqual(
            smb_crunched_3,
            hashlib.sha512("SMBHandle(_source=(SMBSource(_unc=//some/path;_user=egon_olsen));_relpath=filename.file)".encode("unicode_escape")).hexdigest(),  # noqa E501
            "SMBHandle was not crunched correctly.")

    def test_same_path_updates_document_report(self):
        """Ensure that recording matches with handles, where only the _user or
        _driveletter differs, updates the existing report, instead of creating
        a new one."""

        smb_dr_1 = record_match(smb_match_1._replace(handle=smb_match_1.handle.censor()))

        self.assertEqual(DocumentReport.objects.count(), 1)

        smb_dr_2 = record_match(smb_match_2._replace(handle=smb_match_2.handle.censor()))

        self.assertEqual(DocumentReport.objects.count(), 1)
        self.assertEqual(smb_dr_1, smb_dr_2)

        smb_dr_3 = record_match(smb_match_3._replace(handle=smb_match_3.handle.censor()))

        self.assertEqual(DocumentReport.objects.count(), 1)
        self.assertEqual(smb_dr_1.path, smb_dr_3.path)

    def test_missing_file_with_no_previous_report(self):
        """ A problem message containing information about a missing file, with
        no unresolved or resolution_status=0 DocumentReport,
        has no relevance, should be thrown away and not create a new DR."""
        record_problem(deletion)
        self.assertEqual(DocumentReport.objects.count(), 0,
                         "A DocumentReport representing a deleted file was created anyways!")

    def test_requeued_problem_with_existing_report(self):
        """ If exactly the same problem message enters the queue again,
        it should not cause two reports nor crash. """

        record_problem(transient_handle_error)
        # Imagine a world, where the same message enters the queue again:
        record_problem(transient_handle_error)

        # Check that we've only got one DocumentReport
        self.assertEqual(DocumentReport.objects.count(), 1,
                         "Two DocumentReports created for the same handle!")

    def test_requeued_match_with_existing_report(self):
        """ If exactly the same match message enters the queue again,
         it should not cause two reports nor crash. """

        record_match(positive_match)
        # Imagine a world, where the same message enters the queue again:
        record_match(positive_match)
        self.assertEqual(DocumentReport.objects.count(), 1,
                         "Two DocumentReports created for the same handle!")

    def test_reqeued_match_with_existing_false_positive_report(self):
        """If a report has been handled as false positive, receiving the same
        match message again should keep or override the resolution_status,
        dependant on the 'keep_fp'-value received."""

        # Initial match message
        record_match(positive_match)

        # Handle the report as a false positive
        dr = DocumentReport.objects.last()
        dr.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE.value
        dr.save()

        # Another message
        record_match(positive_match_keep_fp)

        # Resolution status should still be the same.
        self.assertEqual(DocumentReport.objects.last().resolution_status,
                         DocumentReport.ResolutionChoices.FALSE_POSITIVE.value,
                         "DocumentReport did not keep its false positive resolution status!")

        # Another message, this time with keep_fp=False
        record_match(positive_match_dont_keep_fp)

        # Resolution status should be None now.
        self.assertEqual(DocumentReport.objects.last().resolution_status, None,
                         "DocumentReport resolution status was not reset!")

    def test_conserve_false_positive_same_message_twice(self):
        """When performing a thorough scan, previously handled reports, which
        are marked as false positive, will be received by the result collector
        twice, because the engine will visit it twice (due to ScheduledCheckups.)
        The status should still be conserved."""

        # Initial match message
        record_match(positive_match)

        # Handle the report as a false positive
        dr = DocumentReport.objects.last()
        dr.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE.value
        dr.save()

        # Another message -- twice
        record_match(positive_match_keep_fp)
        record_match(positive_match_keep_fp)

        # Resolution status should still be the same.
        self.assertEqual(DocumentReport.objects.last().resolution_status,
                         DocumentReport.ResolutionChoices.FALSE_POSITIVE.value,
                         "DocumentReport did not keep its false positive resolution status!")

    def test_override_only_notify_superadmin_with_last_modified_on(self):
        """If a match has been scanned with only_notify_superadmin, and later is scanned without it,
        the DocumentReport should be updated accordingly."""

        record_match(positive_match_only_notify_superadmin)
        before = DocumentReport.objects.last().only_notify_superadmin

        record_match(late_negative_match)
        after = DocumentReport.objects.last().only_notify_superadmin

        self.assertTrue(before)
        self.assertFalse(after)

    def test_only_override_when_only_notify_superadmin_turned_off(self):
        """If a match has been scanned with only_notify_superadmin, scanning it again later,
        shouldn't change only_notify_superadmin."""

        record_match(positive_match_only_notify_superadmin)
        before = DocumentReport.objects.last().only_notify_superadmin

        record_match(positive_match_only_notify_superadmin_later)
        after = DocumentReport.objects.last().only_notify_superadmin

        self.assertTrue(before)
        self.assertTrue(after)

    def test_take_back_results_when_using_only_notify_superadmin(self):
        """Scanning with only_notify_superadmin on, should update previously scanned matches."""

        record_match(positive_match)
        before = DocumentReport.objects.last().only_notify_superadmin

        record_match(positive_match_only_notify_superadmin_later)
        after = DocumentReport.objects.last().only_notify_superadmin

        self.assertFalse(before)
        self.assertTrue(after)
